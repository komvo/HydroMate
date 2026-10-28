package com.hydromate.mobile.ui

import android.animation.ValueAnimator
import android.animation.ObjectAnimator
import android.animation.PropertyValuesHolder
import android.animation.StateListAnimator
import android.app.AlertDialog
import android.content.Context
import android.content.res.Configuration
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.text.SpannableString
import android.text.Spanned
import android.text.style.ForegroundColorSpan
import android.text.style.RelativeSizeSpan
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.widget.*
import com.hydromate.mobile.R
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

class Components(val context: Context) {
    val ink = color(R.color.ink)
    val muted = color(R.color.muted)
    val primary = color(R.color.primary)
    val water = color(R.color.water)
    val backdropInk = color(R.color.backdrop_ink)
    val backdropMuted = color(R.color.backdrop_muted)
    val night = context.resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK == Configuration.UI_MODE_NIGHT_YES
    val largeText get() = context.resources.configuration.fontScale >= 1.3f
    /** Large-title size that never splits a word at 320 dp with font scale 2. */
    fun titleSize(regular: Int) = when {
        context.resources.configuration.fontScale >= 1.7f -> 20
        largeText -> 24
        else -> regular
    }
    val twoColumns get() = context.resources.configuration.screenWidthDp >= 350 && !largeText
    /** Shared per container: one decoded photo and one frosted copy. */
    val backdrop by lazy { GlassBackdrop(this) }
    private val medium = Typeface.create("sans-serif-medium", Typeface.NORMAL)
    fun color(id: Int) = context.getColor(id)
    fun withAlpha(color: Int, alpha: Int) = (color and 0x00FFFFFF) or (alpha shl 24)
    fun dp(value: Int) = (value * context.resources.displayMetrics.density + .5f).toInt()
    fun column() = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL }
    fun row() = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
        clipChildren = false; clipToPadding = false
    }
    fun text(value: String, size: Int = 14, bold: Boolean = false, tint: Int = ink) = TextView(context).apply {
        text = value; textSize = size.toFloat(); setTextColor(tint)
        setPadding(0, dp(2), 0, dp(2))
        if (bold) typeface = if (size >= 20) Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD) else medium
        if (size >= 24) letterSpacing = -.015f
        setLineSpacing(0f, 1.08f)
    }
    /** Text placed directly on the backdrop keeps a soft veil halo behind its glyphs. */
    fun onBackdrop(view: TextView) = view.apply {
        setShadowLayer(dp(8).toFloat(), 0f, 0f, withAlpha(color(R.color.veil), 0xF0))
    }
    fun background(tint: Int, radius: Int = 20) = GradientDrawable().apply {
        setColor(tint); cornerRadius = dp(radius).toFloat()
    }
    fun glass(style: GlassStyle = GlassStyle.PANEL, radius: Int = 26, tint: Int? = null) = GlassSurface(this, style, radius, tint)
    private fun shadow(view: View, elevation: Int) {
        view.elevation = dp(elevation).toFloat()
        if (android.os.Build.VERSION.SDK_INT >= 28) {
            view.outlineAmbientShadowColor = color(R.color.sky_deep)
            view.outlineSpotShadowColor = color(R.color.sky_deep)
        }
    }
    fun surface(tint: Int? = null, radius: Int = 26) = column().apply {
        setPadding(dp(16), dp(14), dp(16), dp(14))
        background = glass(if (tint == null) GlassStyle.PANEL else GlassStyle.TINTED, radius, tint)
        shadow(this, 2)
    }
    fun card(parent: LinearLayout, tint: Int? = null) = surface(tint).apply {
        parent.addView(this, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12); bottomMargin = dp(2) })
    }
    fun image(id: Int, size: Int = 32) = ImageView(context).apply {
        setImageResource(id); scaleType = ImageView.ScaleType.FIT_CENTER
        layoutParams = LinearLayout.LayoutParams(dp(size), dp(size))
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
    }
    fun icon(symbol: GlassSymbol, size: Int = 32) = image(symbol.resource, size)
    /** Icon resting in a small round glass well, concentric with its panel. */
    fun iconWell(symbol: GlassSymbol, size: Int = 30) = FrameLayout(context).apply {
        background = glass(GlassStyle.TINTED, CAPSULE, color(R.color.sky))
        val pad = dp(5); setPadding(pad, pad, pad, pad)
        addView(icon(symbol, size), FrameLayout.LayoutParams(dp(size), dp(size), Gravity.CENTER))
        layoutParams = LinearLayout.LayoutParams(dp(size) + 2 * pad, dp(size) + 2 * pad)
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
    }
    fun portalHeader(parent: LinearLayout, title: String, subtitle: String, symbol: GlassSymbol) {
        val header = row().apply { setPadding(0, dp(8), 0, dp(4)) }
        val copy = column()
        copy.addView(onBackdrop(text(title, titleSize(32), true, backdropInk)).apply {
            if (android.os.Build.VERSION.SDK_INT >= 28) isAccessibilityHeading = true
        })
        copy.addView(onBackdrop(text(subtitle, 15, tint = backdropMuted)))
        header.addView(copy, LinearLayout.LayoutParams(0, -2, 1f))
        if (!largeText) header.addView(icon(symbol, 60))
        parent.addView(header)
    }
    fun badge(value: String, tint: Int = ink, fill: Int = color(R.color.water_soft)) = text(value, 12, true, tint).apply {
        setPadding(dp(11), dp(5), dp(11), dp(5))
        background = glass(GlassStyle.TINTED, CAPSULE, fill)
        layoutParams = LinearLayout.LayoutParams(-2, -2).apply { topMargin = dp(6) }
    }
    fun section(parent: LinearLayout, title: String, subtitle: String? = null, inSurface: Boolean = false) {
        parent.addView(text(title, 20, true, if (inSurface) ink else backdropInk).apply {
            if (!inSurface) onBackdrop(this)
            setPadding(dp(4), dp(22), 0, dp(2))
            val size = dp(16)
            setCompoundDrawablesRelative(LeafGlyph(this@Components).apply { setBounds(0, 0, size, size) }, null, null, null)
            compoundDrawablePadding = dp(8)
            if (android.os.Build.VERSION.SDK_INT >= 28) isAccessibilityHeading = true
        })
        subtitle?.let {
            parent.addView(text(it, 14, tint = if (inSurface) muted else backdropMuted).apply {
                if (!inSurface) onBackdrop(this)
                setPadding(dp(4), 0, 0, 0)
            })
        }
    }
    /** Controls come alive under the finger: a short grow, respecting disabled animators. */
    fun pressable(view: View, lift: Int = 2) {
        shadow(view, lift)
        view.stateListAnimator = if (ValueAnimator.areAnimatorsEnabled()) StateListAnimator().apply {
            addState(intArrayOf(android.R.attr.state_pressed), ObjectAnimator.ofPropertyValuesHolder(view,
                PropertyValuesHolder.ofFloat("scaleX", 1.03f), PropertyValuesHolder.ofFloat("scaleY", 1.03f),
                PropertyValuesHolder.ofFloat("translationZ", dp(3).toFloat())).setDuration(150))
            addState(intArrayOf(), ObjectAnimator.ofPropertyValuesHolder(view,
                PropertyValuesHolder.ofFloat("scaleX", 1f), PropertyValuesHolder.ofFloat("scaleY", 1f),
                PropertyValuesHolder.ofFloat("translationZ", 0f)).setDuration(180))
        } else null
    }
    fun button(label: String, action: () -> Unit, emphasized: Boolean = true) = Button(context).apply {
        text = label; textSize = 15f; isAllCaps = false; typeface = medium
        minHeight = dp(52); minimumHeight = dp(52); minWidth = dp(48)
        setPadding(dp(18), dp(8), dp(18), dp(8))
        background = glass(if (emphasized) GlassStyle.PROMINENT else GlassStyle.CONTROL, CAPSULE)
        backgroundTintList = null
        setTextColor(android.content.res.ColorStateList(
            arrayOf(intArrayOf(-android.R.attr.state_enabled), intArrayOf()),
            intArrayOf(muted, if (emphasized) color(R.color.on_prominent) else ink)))
        pressable(this)
        setOnClickListener { action() }
    }
    fun iconButton(id: Int, label: String, action: () -> Unit) = ImageButton(context).apply {
        setImageResource(id); contentDescription = label
        scaleType = ImageView.ScaleType.FIT_CENTER
        background = glass(GlassStyle.CONTROL, CAPSULE)
        backgroundTintList = null
        setPadding(dp(11), dp(11), dp(11), dp(11))
        pressable(this, 4)
        setOnClickListener { action() }; minimumWidth = dp(52); minimumHeight = dp(52)
    }
    fun actions(parent: LinearLayout, vararg buttons: View) {
        val group = if (largeText) column() else row()
        parent.addView(group, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
        buttons.forEachIndexed { index, button ->
            group.addView(button, LinearLayout.LayoutParams(if (largeText) -1 else 0, -2, if (largeText) 0f else 1f).apply {
                if (index > 0) { if (largeText) topMargin = dp(8) else marginStart = dp(8) }
            })
        }
    }
    /** Inset grouped list: one glass panel, rows separated by hairlines. */
    fun group(parent: LinearLayout) = surface().apply {
        setPadding(dp(16), dp(4), dp(16), dp(4))
        parent.addView(this, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10); bottomMargin = dp(2) })
    }
    fun divider(parent: LinearLayout, inset: Int = 0) = parent.addView(View(context).apply {
        setBackgroundColor(withAlpha(color(R.color.sky_deep), if (night) 0x55 else 0x30))
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
    }, LinearLayout.LayoutParams(-1, maxOf(1, dp(1) / 2)).apply { marginStart = dp(inset) })
    fun listRow(parent: LinearLayout, symbol: GlassSymbol?, title: String, detail: String? = null,
                action: (() -> Unit)? = null): LinearLayout {
        if (parent.childCount > 0) divider(parent, if (symbol != null) 54 else 0)
        val line = row().apply { setPadding(0, dp(12), 0, dp(12)); minimumHeight = dp(56) }
        symbol?.let { line.addView(iconWell(it, 30)) }
        val copy = column()
        copy.addView(text(title, 16, true)); detail?.let { copy.addView(text(it, 14, tint = muted)) }
        line.addView(copy, LinearLayout.LayoutParams(0, -2, 1f).apply { if (symbol != null) marginStart = dp(12) })
        if (action != null) {
            line.addView(text("›", 24, tint = muted).apply { importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO })
            line.isClickable = true; line.isFocusable = true
            line.background = android.graphics.drawable.StateListDrawable().apply {
                addState(intArrayOf(android.R.attr.state_pressed), background(withAlpha(color(R.color.selected), 0x88), 16))
                addState(intArrayOf(android.R.attr.state_focused), background(withAlpha(color(R.color.selected), 0x88), 16))
                addState(intArrayOf(), background(Color.TRANSPARENT))
            }
            line.contentDescription = listOfNotNull(title, detail).joinToString(". ")
            line.setOnClickListener { action() }
        }
        parent.addView(line, LinearLayout.LayoutParams(-1, -2))
        return line
    }
    /** Segmented control: a glass track with a selected lens; reflows to rows with large text. */
    fun segmented(parent: LinearLayout, options: List<String>, selected: Int, perRow: Int,
                  describe: (Int, Boolean) -> String, select: (Int) -> Unit) {
        options.indices.chunked(perRow).forEach { indices ->
            val track = row().apply {
                background = glass(GlassStyle.CONTROL, CAPSULE)
                setPadding(dp(4), dp(4), dp(4), dp(4))
            }
            parent.addView(track, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
            indices.forEach { index ->
                val active = index == selected
                track.addView(text(options[index], 14, active, if (active) primary else ink).apply {
                    gravity = Gravity.CENTER; minHeight = dp(48)
                    setPadding(dp(4), dp(6), dp(4), dp(6))
                    background = if (active) glass(GlassStyle.SELECTED, CAPSULE) else
                        android.graphics.drawable.StateListDrawable().apply {
                            addState(intArrayOf(android.R.attr.state_pressed), background(withAlpha(color(R.color.selected), 0x99), 22))
                            addState(intArrayOf(android.R.attr.state_focused), background(withAlpha(color(R.color.selected), 0x99), 22))
                            addState(intArrayOf(), background(Color.TRANSPARENT))
                        }
                    isClickable = true; isFocusable = true; isSelected = active
                    contentDescription = describe(index, active)
                    setOnClickListener { select(index) }
                }, LinearLayout.LayoutParams(0, -2, 1f))
            }
        }
    }
    /** Large tabular value with a smaller unit, as in a glanceable widget. */
    fun metric(value: String, unit: String, size: Int = 32) = text("", size, true).apply {
        val label = if (unit.isEmpty() || value == "—") value else "$value $unit"
        text = SpannableString(label).apply {
            if (label.length > value.length) {
                setSpan(RelativeSizeSpan(.5f), value.length, label.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                setSpan(ForegroundColorSpan(muted), value.length, label.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            }
        }
        fontFeatureSettings = "tnum"
    }
    fun disclosure(parent: LinearLayout, title: String, expanded: Boolean = false,
                   changed: (Boolean) -> Unit = {}, body: (LinearLayout) -> Unit) {
        val content = column().apply { visibility = if (expanded) View.VISIBLE else View.GONE }
        var open = expanded
        val toggle = button(context.getString(if (open) R.string.hide_details else R.string.show_details, title), {}, false)
        toggle.setOnClickListener {
            open = !open; content.visibility = if (open) View.VISIBLE else View.GONE
            toggle.text = context.getString(if (open) R.string.hide_details else R.string.show_details, title)
            changed(open)
        }
        parent.addView(toggle, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(8) })
        body(content); parent.addView(content)
    }
    fun help(title: String, message: String) {
        AlertDialog.Builder(context).setTitle(title).setMessage(message).setPositiveButton("Entendido", null).show()
    }
    fun fade(view: View) {
        if (ValueAnimator.areAnimatorsEnabled()) {
            view.alpha = .5f; view.translationY = dp(6).toFloat()
            view.animate().alpha(1f).translationY(0f).setDuration(180).start()
        }
    }
    fun number(value: Double) = String.format(Locale.getDefault(), "%.2f", value)
    fun date(value: Instant) = DateTimeFormatter.ofPattern("dd MMM yyyy · HH:mm:ss", Locale.getDefault())
        .withZone(ZoneId.systemDefault()).format(value)
}

/**
 * Screen container shared by MainActivity and the debug visual review: botanical backdrop,
 * scroll content with a top scroll-edge fade, and navigation floating in its own glass layer.
 */
class GlassScaffold(val ui: Components) : FrameLayout(ui.context) {
    constructor(context: Context) : this(Components(context))
    val provenance = ui.column()
    val scroll = RefreshScrollView(ui.context).apply { isFillViewport = true; isVerticalScrollBarEnabled = false }
    val content = ui.column().apply { setPadding(ui.dp(16), ui.dp(8), ui.dp(16), ui.dp(24)) }
    val navigation = AeroBottomNavigation(ui)
    init {
        background = AeroSky(ui)
        ui.backdrop.attach(this)
        val stack = ui.column()
        stack.addView(provenance, LinearLayout.LayoutParams(-1, -2).apply { setMargins(ui.dp(16), ui.dp(4), ui.dp(16), 0) })
        val viewport = FrameLayout(ui.context)
        scroll.addView(content)
        viewport.addView(scroll, LayoutParams(-1, -1))
        // Scroll edge effect: content softens into the veil instead of being cut at the top.
        viewport.addView(View(ui.context).apply {
            background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                intArrayOf(ui.withAlpha(ui.color(R.color.veil), 0xD8), Color.TRANSPARENT))
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }, LayoutParams(-1, ui.dp(18), Gravity.TOP))
        stack.addView(viewport, LinearLayout.LayoutParams(-1, 0, 1f))
        addView(stack, LayoutParams(-1, -1))
        val side = if (ui.context.resources.configuration.fontScale >= 1.5f) ui.dp(8) else ui.dp(14)
        addView(navigation, LayoutParams(-1, -2, Gravity.BOTTOM).apply { setMargins(side, 0, side, ui.dp(10)) })
    }
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Content may scroll beneath the floating bar but always ends above it; set before measuring.
        val wanted = if (navigation.visibility == View.VISIBLE) {
            measureChildWithMargins(navigation, widthMeasureSpec, 0, heightMeasureSpec, 0)
            navigation.measuredHeight + ui.dp(10) + ui.dp(24)
        } else ui.dp(24)
        if (content.paddingBottom != wanted) content.setPadding(content.paddingLeft, content.paddingTop, content.paddingRight, wanted)
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }
}

class RefreshScrollView(context: Context) : ScrollView(context) {
    var onRefresh: (() -> Unit)? = null
    private var startX = 0f
    private var startY = 0f
    private var atTop = false
    override fun performClick(): Boolean = super.performClick()
    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        if (event.actionMasked == MotionEvent.ACTION_DOWN) {
            startX = event.x; startY = event.y; atTop = scrollY == 0
        }
        if (event.actionMasked == MotionEvent.ACTION_MOVE && atTop && onRefresh != null
            && event.y - startY > 100 * resources.displayMetrics.density
            && kotlin.math.abs(event.x - startX) < 50 * resources.displayMetrics.density) return true
        return super.onInterceptTouchEvent(event)
    }
    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.actionMasked == MotionEvent.ACTION_UP && atTop && onRefresh != null
            && event.y - startY > 100 * resources.displayMetrics.density
            && kotlin.math.abs(event.x - startX) < 50 * resources.displayMetrics.density) {
            atTop = false; onRefresh?.invoke(); performClick(); return true
        }
        return super.onTouchEvent(event)
    }
}
