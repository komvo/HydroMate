package com.hydromate.mobile.ui

import android.graphics.Color
import android.graphics.drawable.StateListDrawable
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import com.hydromate.mobile.R

/** Shared by the app and the explicit debug visual review. */
class AeroBottomNavigation(private val ui: Components) : LinearLayout(ui.context) {
    constructor(context: android.content.Context) : this(Components(context))
    init {
        orientation = HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
        clipChildren = false; clipToPadding = false
        background = AeroSurface(ui, ui.color(R.color.sky), true, radius = 22)
        setPadding(ui.dp(4), ui.dp(7), ui.dp(4), ui.dp(5))
        elevation = ui.dp(8).toFloat()
    }
    fun show(destination: Destination, navigate: (Destination) -> Unit) {
        removeAllViews()
        Destination.entries.forEach { item ->
            val selected = destination == item
            val tab = ui.column().apply {
                gravity = Gravity.CENTER; minimumHeight = ui.dp(64)
                val holder = ui.row().apply {
                    gravity = Gravity.CENTER
                    if (selected) background = AeroSurface(ui, ui.color(R.color.aqua), true, 20)
                    addView(ui.image(item.icon.navigationResource, if (item == Destination.CULTIVATION) 34 else 36))
                }
                addView(holder, LayoutParams(ui.dp(56), ui.dp(38)).apply { gravity = Gravity.CENTER_HORIZONTAL })
                val enlarged = ui.context.resources.configuration.fontScale >= 1.5f
                val label = if (enlarged && item == Destination.HISTORY) "Hist." else item.title
                addView(ui.text(label, if (enlarged) 9 else 11, selected).apply {
                    gravity = Gravity.CENTER; importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
                }, LayoutParams(-1, -2))
                isSelected = selected; isFocusable = true; isClickable = true
                background = StateListDrawable().apply {
                    addState(intArrayOf(android.R.attr.state_focused), AeroSurface(ui, ui.color(R.color.water_soft), radius = 14))
                    addState(intArrayOf(android.R.attr.state_pressed), ui.background(ui.color(R.color.water_soft), 14))
                    addState(intArrayOf(), ui.background(Color.TRANSPARENT))
                }
                contentDescription = "${item.title}${if (selected) ", seleccionado" else ""}"
                setOnClickListener { navigate(item) }
            }
            addView(tab, LayoutParams(0, -2, 1f))
        }
    }
}
