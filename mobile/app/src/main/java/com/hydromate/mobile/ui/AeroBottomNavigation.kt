package com.hydromate.mobile.ui

import android.graphics.Color
import android.graphics.drawable.StateListDrawable
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import com.hydromate.mobile.R

/** Floating capsule tab bar in the glass controls layer; the selected tab rests in a lens. */
class AeroBottomNavigation(private val ui: Components) : LinearLayout(ui.context) {
    constructor(context: android.content.Context) : this(Components(context))
    init {
        orientation = HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
        clipChildren = false; clipToPadding = false
        background = ui.glass(GlassStyle.CONTROL, CAPSULE)
        val pad = if (ui.context.resources.configuration.fontScale >= 1.5f) ui.dp(3) else ui.dp(5)
        setPadding(pad, pad, pad, pad)
        elevation = ui.dp(10).toFloat()
        if (android.os.Build.VERSION.SDK_INT >= 28) {
            outlineAmbientShadowColor = ui.color(R.color.sky_deep); outlineSpotShadowColor = ui.color(R.color.sky_deep)
        }
    }
    fun show(destination: Destination, navigate: (Destination) -> Unit) {
        removeAllViews()
        Destination.entries.forEach { item ->
            val selected = destination == item
            val tab = ui.column().apply {
                gravity = Gravity.CENTER; minimumHeight = ui.dp(58)
                setPadding(0, ui.dp(5), 0, ui.dp(4))
                addView(ui.image(item.icon.navigationResource, if (item == Destination.CULTIVATION) 28 else 30).apply {
                    layoutParams = LayoutParams(ui.dp(30), ui.dp(30)).apply { gravity = Gravity.CENTER_HORIZONTAL }
                })
                val enlarged = ui.context.resources.configuration.fontScale >= 1.5f
                val label = if (enlarged && item == Destination.HISTORY) "Hist." else item.title
                addView(ui.text(label, if (enlarged) 8 else 11, selected, if (selected) ui.primary else ui.ink).apply {
                    gravity = Gravity.CENTER; setPadding(0, 0, 0, 0); maxLines = 1
                    importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
                }, LayoutParams(-1, -2))
                isSelected = selected; isFocusable = true; isClickable = true
                background = if (selected) ui.glass(GlassStyle.SELECTED, CAPSULE) else StateListDrawable().apply {
                    addState(intArrayOf(android.R.attr.state_focused), ui.glass(GlassStyle.SELECTED, CAPSULE))
                    addState(intArrayOf(android.R.attr.state_pressed), ui.background(ui.withAlpha(ui.color(R.color.selected), 0x99), 29))
                    addState(intArrayOf(), ui.background(Color.TRANSPARENT))
                }
                contentDescription = "${item.title}${if (selected) ", seleccionado" else ""}"
                setOnClickListener { navigate(item) }
            }
            addView(tab, LayoutParams(0, -2, 1f))
        }
    }
}
