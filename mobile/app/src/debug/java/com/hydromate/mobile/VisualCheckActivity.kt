package com.hydromate.mobile

import android.app.Activity
import android.content.Context
import android.content.res.Configuration
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.*
import com.hydromate.mobile.ui.*
import com.hydromate.mobile.ui.dashboard.DashboardScreen
import com.hydromate.mobile.ui.history.HistoryScreen
import com.hydromate.mobile.ui.history.Metric
import com.hydromate.mobile.ui.cultivation.CultivationScreen
import com.hydromate.mobile.ui.control.ControlScreen
import com.hydromate.mobile.ui.settings.*
import org.json.JSONArray
import org.json.JSONObject

/**
 * Explicit debug-only layout review. No repository, preferences, real data, or commands.
 * Configuration applies only to this Activity; it never changes phone settings.
 * This does not verify touch injection, lifecycle networking, TalkBack or the IME.
 */
class VisualCheckActivity : Activity() {
    private lateinit var ui: Components
    private lateinit var frame: LinearLayout
    private lateinit var body: LinearLayout
    private lateinit var nav: AeroBottomNavigation
    private lateinit var scroll: ScrollView
    private var screen = Destination.HOME
    private var scenario = 1
    private var metric = Metric.PH
    private var expanded = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Keep this explicit review visible; does not wake/unlock or change system settings.
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        val width = intent.getIntExtra("width_dp", 393).coerceIn(320, 900)
        val font = intent.getFloatExtra("font_scale", 1f).coerceIn(1f, 2f)
        val night = intent.getBooleanExtra("night", false)
        val configuration = Configuration(resources.configuration).apply {
            screenWidthDp = width
            densityDpi = (resources.displayMetrics.widthPixels * 160f / width).toInt()
            fontScale = font
            uiMode = (uiMode and Configuration.UI_MODE_NIGHT_MASK.inv()) or
                if (night) Configuration.UI_MODE_NIGHT_YES else Configuration.UI_MODE_NIGHT_NO
        }
        val reviewContext: Context = android.view.ContextThemeWrapper(createConfigurationContext(configuration), R.style.AppTheme)
        ui = Components(reviewContext)
        screen = Destination.entries.find { it.name == intent.getStringExtra("screen") } ?: Destination.HOME
        scenario = intent.getIntExtra("scenario", 1).coerceIn(1, 7)
        frame = ui.column().apply { background = AeroSky(ui) }
        frame.addView(ui.badge("Prueba visual · datos simulados").apply { gravity = Gravity.CENTER })
        scroll = ScrollView(reviewContext).apply { isFillViewport = true }
        body = ui.column().apply { setPadding(ui.dp(16), ui.dp(12), ui.dp(16), ui.dp(24)) }
        scroll.addView(body)
        frame.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        nav = AeroBottomNavigation(ui)
        frame.addView(nav)
        setContentView(frame)
        @Suppress("DEPRECATION")
        window.statusBarColor = ui.color(R.color.background)
        @Suppress("DEPRECATION")
        window.navigationBarColor = ui.color(R.color.background)
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = if (night) 0 else View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
        render()
    }

    private fun render() {
        body.removeAllViews()
        val state = PreviewSupport.load(scenario)!!
        fun move(next: Destination) { screen = next; scroll.scrollTo(0, 0); render() }
        val settings = { move(Destination.SETTINGS) }
        when (screen) {
            Destination.HOME -> DashboardScreen(ui).render(body, state, "Torre de demostración",
                PreviewSupport.referenceAge(scenario, 0), { render() }, settings,
                { move(Destination.CULTIVATION) }, { move(Destination.CONTROL) })
            Destination.HISTORY -> HistoryScreen(ui).render(body, state, metric, { metric = it; render() }, { render() }, settings)
            Destination.CULTIVATION -> CultivationScreen(ui).render(body)
            Destination.CONTROL -> ControlScreen(ui).render(body, { move(Destination.HOME) }, expanded, { expanded = it })
            Destination.SETTINGS -> SettingsScreen(ui).render(body,
                ConnectionDraft("http://127.0.0.1:8000", "test-demo-aero", "Torre de demostración", "0"), state,
                { ui.help("Prueba visual", "Esta vista no guarda configuración ni consulta servidores.") },
                { move(Destination.CONTROL) }, "aero",
                { ui.help("Prueba visual", "La apariencia de esta vista se elige al iniciar la revisión.") },
                scenario, { if (it > 0) { scenario = it; render() } else finish() }, emptyList(), {})
        }
        nav.show(screen, ::move)
        frame.post {
            if (intent.getBooleanExtra("bottom", false)) scroll.fullScroll(View.FOCUS_DOWN)
            auditLayout()
        }
    }

    private fun auditLayout() {
        val textIssues = JSONArray()
        val targets = JSONArray()
        fun inspect(view: View) {
            if (view.visibility != View.VISIBLE) return
            if (view is TextView && view.width > 0) view.layout?.let { layout ->
                val available = view.width - view.compoundPaddingLeft - view.compoundPaddingRight
                // EditText deliberately scrolls horizontally; trailing whitespace has no painted glyphs.
                val overflow = view !is EditText && (0 until layout.lineCount).any {
                    layout.getLineMax(it) > available + 2 || layout.getEllipsisCount(it) > 0
                }
                if (overflow || layout.height > view.height - view.compoundPaddingTop - view.compoundPaddingBottom + 2)
                    textIssues.put(JSONObject().put("text", view.text.toString()).put("width", view.width).put("height", view.height))
            }
            if (view.isClickable && view.width > 0) targets.put(JSONObject()
                .put("label", view.contentDescription ?: (view as? TextView)?.text ?: view.javaClass.simpleName)
                .put("width_dp", view.width / resourcesDensity())
                .put("height_dp", view.height / resourcesDensity()))
            if (view is ViewGroup) for (index in 0 until view.childCount) inspect(view.getChildAt(index))
        }
        inspect(frame)
        val report = JSONObject().put("screen", screen.name).put("scenario", scenario)
            .put("width_dp", ui.context.resources.configuration.screenWidthDp)
            .put("font_scale", ui.context.resources.configuration.fontScale)
            .put("two_columns", ui.twoColumns).put("night", ui.night)
            .put("text_issues", textIssues).put("touch_targets", targets)
            .put("scope", "Native Android layout review; no network, preferences, injected input or physical states")
        getExternalFilesDir(null)?.resolve("visual-check.json")?.writeText(report.toString(2))
    }
    private fun resourcesDensity() = ui.context.resources.displayMetrics.density
}
