package com.hydromate.mobile

import android.app.Activity
import android.content.Context
import android.content.res.Configuration
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.WindowInsets
import android.widget.LinearLayout
import com.hydromate.mobile.ui.*
import com.hydromate.mobile.ui.dashboard.DashboardScreen
import com.hydromate.mobile.ui.history.HistoryScreen
import com.hydromate.mobile.ui.history.Metric
import com.hydromate.mobile.ui.cultivation.CultivationScreen
import com.hydromate.mobile.ui.control.ControlScreen
import com.hydromate.mobile.ui.settings.*
import java.time.Instant
import java.util.concurrent.Executors
import java.util.concurrent.Future

class MainActivity : Activity() {
    private val executor = Executors.newSingleThreadExecutor()
    private var pending: Future<*>? = null
    private val repository = TelemetryRepository()
    private val requests = RequestFence()
    private var active = false
    private var state: ReadingState = ReadingState.Idle
    private var destination = Destination.HOME
    private var controlOrigin = Destination.HOME
    private var controlExpanded = false
    private var metric = Metric.PH
    private var scenario = 0
    private var appearance = "aero"
    private lateinit var connections: ConnectionStore
    private lateinit var config: ConnectionSettings
    private lateinit var draft: ConnectionDraft
    private lateinit var ui: Components
    private lateinit var content: LinearLayout
    private lateinit var navigation: AeroBottomNavigation
    private lateinit var provenance: LinearLayout
    private lateinit var scroll: RefreshScrollView
    private lateinit var settings: SettingsScreen

    override fun attachBaseContext(newBase: Context) {
        val mode = newBase.getSharedPreferences("appearance", MODE_PRIVATE).getString("mode", "aero")
        val configured = Configuration(newBase.resources.configuration)
        if (mode == "aero") configured.uiMode = (configured.uiMode and Configuration.UI_MODE_NIGHT_MASK.inv()) or Configuration.UI_MODE_NIGHT_NO
        super.attachBaseContext(newBase.createConfigurationContext(configured))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ui = Components(this)
        settings = SettingsScreen(ui)
        appearance = getSharedPreferences("appearance", MODE_PRIVATE).getString("mode", "aero")!!
        // The previous app followed the system without a saved preference.
        getSharedPreferences("appearance", MODE_PRIVATE).edit().putString("previous_default", "system").apply()
        connections = ConnectionStore(this)
        config = connections.current()
        connections.save(config)
        draft = ConnectionDraft(savedInstanceState?.getString("draft_server") ?: config.server,
            savedInstanceState?.getString("draft_device") ?: config.device,
            savedInstanceState?.getString("draft_name") ?: config.name,
            savedInstanceState?.getString("draft_age_text") ?: config.ageMinutes.toString())
        destination = Destination.entries.find { it.name == savedInstanceState?.getString("destination_name") } ?: Destination.HOME
        controlOrigin = Destination.entries.find { it.name == savedInstanceState?.getString("control_origin") } ?: Destination.HOME
        controlExpanded = savedInstanceState?.getBoolean("control_expanded") ?: false
        settings.advanced = savedInstanceState?.getBoolean("advanced") ?: false
        settings.diagnostics = savedInstanceState?.getBoolean("diagnostics") ?: false
        metric = Metric.entries.getOrElse(savedInstanceState?.getInt("metric") ?: 0) { Metric.PH }
        scenario = (savedInstanceState?.getInt("scenario") ?: 0).takeIf { it in PreviewSupport.options.indices } ?: 0
        state = PreviewSupport.load(scenario) ?: ReadingState.Idle
        if (scenario == 0) savedInstanceState?.getString("failure_kind")?.let { kind ->
            FailureKind.entries.find { it.name == kind }?.let {
                state = ReadingState.Failed(it, savedInstanceState.getString("failure_detail").orEmpty())
            }
        }
        val frame = ui.column().apply { background = AeroSky(ui) }
        provenance = ui.column()
        frame.addView(provenance)
        scroll = RefreshScrollView(this).apply { isFillViewport = true }
        content = ui.column().apply { setPadding(ui.dp(16), ui.dp(12), ui.dp(16), ui.dp(24)) }
        scroll.addView(content)
        frame.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        navigation = AeroBottomNavigation(ui)
        frame.addView(navigation, LinearLayout.LayoutParams(-1, -2))
        configureInsets(frame)
        setContentView(frame)
        frame.requestApplyInsets()
        if (Build.VERSION.SDK_INT >= 33) onBackInvokedDispatcher.registerOnBackInvokedCallback(
            android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, ::goBack)
        render()
    }

    @Suppress("DEPRECATION")
    private fun configureInsets(frame: View) {
        if (Build.VERSION.SDK_INT >= 30) {
            window.setDecorFitsSystemWindows(false)
        }
        else window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_LAYOUT_STABLE or
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION or
            (if (ui.night) 0 else View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR)
        frame.setOnApplyWindowInsetsListener { _, insets ->
            if (Build.VERSION.SDK_INT >= 30) {
                val lightBars = android.view.WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS or
                    android.view.WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS
                frame.windowInsetsController?.setSystemBarsAppearance(if (ui.night) 0 else lightBars, lightBars)
                val bars = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout() or WindowInsets.Type.ime())
                frame.setPadding(bars.left, bars.top, bars.right, bars.bottom)
                navigation.visibility = if (insets.isVisible(WindowInsets.Type.ime())) View.GONE else View.VISIBLE
            } else frame.setPadding(insets.systemWindowInsetLeft, insets.systemWindowInsetTop,
                insets.systemWindowInsetRight, insets.systemWindowInsetBottom)
            insets
        }
    }

    override fun onStart() {
        super.onStart(); active = true
        if (state == ReadingState.Idle) refresh()
        else presentState()
    }

    private fun captureDraft() {
        if (destination == Destination.SETTINGS) settings.draft()?.let { draft = it }
    }
    private fun navigate(next: Destination) {
        captureDraft()
        if (next == Destination.CONTROL && destination != Destination.CONTROL) controlOrigin = destination
        destination = next
        scroll.scrollTo(0, 0); render(); ui.fade(content)
        if (state == ReadingState.Idle && next in listOf(Destination.HOME, Destination.HISTORY)) refresh()
    }
    private fun goBack() {
        when (destination) {
            Destination.CONTROL -> navigate(controlOrigin)
            Destination.HOME -> finish()
            else -> navigate(Destination.HOME)
        }
    }
    @Deprecated("Compatibility callback below Android 13")
    override fun onBackPressed() = goBack()
    private fun invalidateRequest() {
        requests.invalidate(); pending?.cancel(true); pending = null
    }
    private fun saveConnection() {
        captureDraft()
        val validated = try { draft.validated() } catch (error: IllegalArgumentException) {
            ui.help("Revisa la configuración", error.message.orEmpty()); return
        }
        invalidateRequest(); config = validated; connections.save(config)
        state = if (scenario > 0) PreviewSupport.load(scenario)!! else ReadingState.Idle
        if (scenario == 0) refresh() else settings.updateState(state, true)
    }
    private fun selectSavedTower(value: ConnectionSettings) {
        captureDraft(); invalidateRequest()
        config = value; draft = value.draft(); connections.save(value)
        state = if (scenario > 0) PreviewSupport.load(scenario)!! else ReadingState.Idle
        render()
        if (scenario == 0) refresh()
    }
    private fun selectScenario(value: Int) {
        captureDraft(); invalidateRequest(); scenario = value
        state = PreviewSupport.load(scenario) ?: ReadingState.Idle
        render()
        if (scenario == 0) refresh()
    }
    private fun requestIdentity() = "${config.server}\n${config.device}"
    private fun refresh() {
        if (!active || (state is ReadingState.Loading && scenario == 0)) return
        if (scenario > 0) {
            state = PreviewSupport.load(scenario)!!; presentState(); return
        }
        val endpoint = try { Telemetry.endpoint(config.server, config.device) }
        catch (error: IllegalArgumentException) {
            state = ReadingState.Failed(FailureKind.ADDRESS, error.message.orEmpty()); presentState(); return
        }
        state = ReadingState.Loading; presentState()
        val ticket = requests.begin(requestIdentity())
        val requestedDevice = config.device
        pending = executor.submit {
            val result = runCatching { repository.load(endpoint, requestedDevice) }
            runOnUiThread {
                if (!active || isDestroyed || isFinishing || scenario != 0 || !requests.accepts(ticket, requestIdentity())) return@runOnUiThread
                state = result.fold(onSuccess = { values ->
                    if (values.isEmpty()) ReadingState.Empty(Instant.now()) else ReadingState.Ready(values, Instant.now())
                }, onFailure = ::failure)
                presentState()
            }
        }
    }
    private fun presentState() {
        // Network results must not replace an active EditText or dismiss its keyboard.
        if (destination == Destination.SETTINGS) {
            settings.updateState(state, scenario > 0); renderProvenance()
        } else render()
    }
    private fun renderProvenance() {
        provenance.removeAllViews()
        val message = when {
            scenario > 0 -> "Demostración · datos simulados"
            config.device.startsWith("test-") || (state as? ReadingState.Ready)?.values?.any { it.synthetic } == true -> "Datos de prueba · ${config.device}"
            (state as? ReadingState.Ready)?.values?.any { it.sources.values.any { source -> source == "simulated" } } == true -> "Contiene variables simuladas · ${config.device}"
            else -> null
        }
        provenance.visibility = if (message == null) View.GONE else View.VISIBLE
        if (message != null) provenance.addView(ui.badge(message).apply {
            gravity = Gravity.CENTER; accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
        }, LinearLayout.LayoutParams(-1, -2))
    }
    private fun render() {
        content.removeAllViews(); renderProvenance()
        scroll.onRefresh = if (destination in listOf(Destination.HOME, Destination.HISTORY)) ({ refresh() }) else null
        when (destination) {
            Destination.HOME -> DashboardScreen(ui).render(content, state,
                if (scenario > 0) "Torre de demostración" else config.name,
                PreviewSupport.referenceAge(scenario, config.ageMinutes),
                ::refresh, { navigate(Destination.SETTINGS) }, { navigate(Destination.CULTIVATION) }, { navigate(Destination.CONTROL) })
            Destination.HISTORY -> HistoryScreen(ui).render(content, state, metric, { metric = it; render() },
                ::refresh, { navigate(Destination.SETTINGS) })
            Destination.CULTIVATION -> CultivationScreen(ui).render(content)
            Destination.CONTROL -> ControlScreen(ui).render(content, ::goBack, controlExpanded, { controlExpanded = it })
            Destination.SETTINGS -> settings.render(content, draft, state, ::saveConnection,
                { navigate(Destination.CONTROL) }, appearance, { value ->
                    captureDraft()
                    getSharedPreferences("appearance", MODE_PRIVATE).edit().putString("mode", value).apply()
                    recreate()
                }, scenario, ::selectScenario, connections.saved(), ::selectSavedTower)
        }
        navigation.show(destination, ::navigate)
    }
    override fun onSaveInstanceState(outState: Bundle) {
        captureDraft()
        outState.putString("draft_server", draft.server); outState.putString("draft_device", draft.device)
        outState.putString("draft_name", draft.name); outState.putString("draft_age_text", draft.age)
        outState.putString("destination_name", destination.name); outState.putString("control_origin", controlOrigin.name)
        outState.putBoolean("control_expanded", controlExpanded)
        outState.putBoolean("advanced", settings.advanced); outState.putBoolean("diagnostics", settings.diagnostics)
        outState.putInt("metric", metric.ordinal); outState.putInt("scenario", scenario)
        (state as? ReadingState.Failed)?.let {
            outState.putString("failure_kind", it.kind.name); outState.putString("failure_detail", it.detail)
        }
        super.onSaveInstanceState(outState)
    }
    override fun onStop() {
        captureDraft(); active = false; invalidateRequest()
        if (state is ReadingState.Loading && scenario == 0) state = ReadingState.Idle
        super.onStop()
    }
    override fun onDestroy() {
        executor.shutdownNow(); super.onDestroy()
    }
}
