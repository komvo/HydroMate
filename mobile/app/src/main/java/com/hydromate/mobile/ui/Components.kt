package com.hydromate.mobile.ui

import android.animation.ValueAnimator
import android.animation.ObjectAnimator
import android.animation.StateListAnimator
import android.app.AlertDialog
import android.content.Context
import android.content.res.Configuration
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
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
    val twoColumns get() = context.resources.configuration.screenWidthDp >= 350 && !largeText
    fun color(id: Int) = context.getColor(id)
    fun dp(value: Int) = (value * context.resources.displayMetrics.density + .5f).toInt()
    fun column() = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL }
    fun row() = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
        clipChildren = false; clipToPadding = false
    }
    fun text(value: String, size: Int = 14, bold: Boolean = false, tint: Int = ink) = TextView(context).apply {
        text = value; textSize = size.toFloat(); setTextColor(tint)
        setPadding(0, dp(2), 0, dp(2))
        if (bold) setTypeface(typeface, Typeface.BOLD)
    }
    fun background(tint: Int, radius: Int = 20) = GradientDrawable().apply {
        setColor(tint); cornerRadius = dp(radius).toFloat()
    }
    fun surface(tint: Int = color(R.color.glass)) = column().apply {
        setPadding(dp(14), dp(12), dp(14), dp(12))
        background = AeroSurface(this@Components, tint)
        elevation = dp(3).toFloat()
        if (android.os.Build.VERSION.SDK_INT >= 28) {
            outlineAmbientShadowColor = color(R.color.sky_deep)
            outlineSpotShadowColor = color(R.color.ink)
        }
    }
    fun card(parent: LinearLayout, tint: Int = color(R.color.glass)) = surface(tint).apply {
        parent.addView(this, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12); bottomMargin = dp(2) })
    }
    fun image(id: Int, size: Int = 32) = ImageView(context).apply {
        setImageResource(id); scaleType = ImageView.ScaleType.FIT_CENTER
        layoutParams = LinearLayout.LayoutParams(dp(size), dp(size))
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
    }
    fun icon(symbol: GlassSymbol, size: Int = 32) = ImageView(context).apply {
        setImageResource(symbol.resource)
        scaleType = ImageView.ScaleType.FIT_CENTER
        layoutParams = LinearLayout.LayoutParams(dp(size), dp(size))
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
    }
    fun portalHeader(parent: LinearLayout, title: String, subtitle: String, symbol: GlassSymbol) {
        val header = row()
        if (!largeText) header.addView(icon(symbol, 68))
        val copy = column()
        copy.addView(text(title, if (largeText) 22 else 26, true, backdropInk))
        copy.addView(text(subtitle, 14, tint = backdropMuted))
        header.addView(copy, LinearLayout.LayoutParams(0, -2, 1f).apply { if (!largeText) marginStart = dp(10) })
        parent.addView(header)
    }
    fun badge(value: String, tint: Int = ink, fill: Int = color(R.color.water_soft)) = text(value, 12, true, tint).apply {
        setPadding(dp(10), dp(6), dp(10), dp(6)); background = AeroSurface(this@Components, fill, glossy = true, radius = 12)
    }
    fun section(parent: LinearLayout, title: String, subtitle: String? = null, inSurface: Boolean = false) {
        parent.addView(text(title, 20, true, if (inSurface) ink else backdropInk).apply {
            setPadding(0, dp(18), 0, dp(4))
            if (android.os.Build.VERSION.SDK_INT >= 28) isAccessibilityHeading = true
        })
        subtitle?.let { parent.addView(text(it, 14, tint = if (inSurface) muted else backdropMuted)) }
    }
    fun button(label: String, action: () -> Unit, emphasized: Boolean = true) = Button(context).apply {
        text = label; textSize = 14f; isAllCaps = false
        minHeight = dp(52); minimumHeight = dp(52); minWidth = dp(48)
        setPadding(dp(14), dp(8), dp(14), dp(8))
        background = AeroSurface(this@Components, color(if (emphasized) R.color.lime else R.color.water_soft), true, 26)
        backgroundTintList = null
        setTextColor(android.content.res.ColorStateList(
            arrayOf(intArrayOf(-android.R.attr.state_enabled), intArrayOf()),
            intArrayOf(muted, ink)))
        elevation = dp(2).toFloat()
        val target = this
        stateListAnimator = if (ValueAnimator.areAnimatorsEnabled()) StateListAnimator().apply {
            addState(intArrayOf(android.R.attr.state_pressed), ObjectAnimator.ofFloat(target, "translationZ", -dp(1).toFloat()).setDuration(150))
            addState(intArrayOf(), ObjectAnimator.ofFloat(target, "translationZ", 0f).setDuration(150))
        } else null
        setOnClickListener { action() }
    }
    fun iconButton(id: Int, label: String, action: () -> Unit) = ImageButton(context).apply {
        setImageResource(id); contentDescription = label
        scaleType = ImageView.ScaleType.FIT_CENTER
        background = AeroSurface(this@Components, color(R.color.water_soft), true, 26)
        backgroundTintList = null
        setPadding(dp(9), dp(9), dp(9), dp(9))
        setOnClickListener { action() }; minimumWidth = dp(52); minimumHeight = dp(52)
    }
    fun actions(parent: LinearLayout, vararg buttons: View) {
        val group = if (largeText) column() else row()
        parent.addView(group, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(8) })
        buttons.forEachIndexed { index, button ->
            group.addView(button, LinearLayout.LayoutParams(if (largeText) -1 else 0, -2, if (largeText) 0f else 1f).apply {
                if (index > 0) { if (largeText) topMargin = dp(8) else marginStart = dp(8) }
            })
        }
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
        parent.addView(toggle, LinearLayout.LayoutParams(-1, -2))
        body(content); parent.addView(content)
    }
    fun help(title: String, message: String) {
        AlertDialog.Builder(context).setTitle(title).setMessage(message).setPositiveButton("Entendido", null).show()
    }
    fun fade(view: View) {
        if (ValueAnimator.areAnimatorsEnabled()) {
            view.alpha = .5f; view.animate().alpha(1f).setDuration(180).start()
        }
    }
    fun number(value: Double) = String.format(Locale.getDefault(), "%.2f", value)
    fun date(value: Instant) = DateTimeFormatter.ofPattern("dd MMM yyyy · HH:mm:ss", Locale.getDefault())
        .withZone(ZoneId.systemDefault()).format(value)
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
