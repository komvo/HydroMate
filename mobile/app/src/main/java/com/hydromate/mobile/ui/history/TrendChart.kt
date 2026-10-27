package com.hydromate.mobile.ui.history

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.*
import android.view.MotionEvent
import android.view.View
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.Components
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

/**
 * Line-and-area trend with a dynamic axis, average rule, visible gaps and the newest
 * point emphasised. In [compact] mode it is a decorative sparkline without axes.
 * Dragging in full mode reports the nearest sample to [onInspect]; null on release.
 */
class TrendChart @JvmOverloads constructor(
    context: Context, private val samples: List<Sample> = emptyList(), private val metric: Metric = Metric.PH,
    private val compact: Boolean = false, private val ui: Components = Components(context),
    private val onInspect: (Sample?) -> Unit = {}
) : View(context) {
    private val segments = TrendMath.segments(samples)
    private val values = samples.map { it.value }
    private val ticks = if (values.isEmpty()) emptyList() else TrendMath.ticks(values)
    private val average = if (values.isEmpty()) 0.0 else values.average()
    private val line = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE; strokeWidth = ui.dp(if (compact) 2 else 3).toFloat()
        strokeCap = Paint.Cap.ROUND; strokeJoin = Paint.Join.ROUND
    }
    private val fill = Paint(Paint.ANTI_ALIAS_FLAG)
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val label = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = android.util.TypedValue.applyDimension(android.util.TypedValue.COMPLEX_UNIT_SP, 11f, resources.displayMetrics); color = ui.muted
        typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL); fontFeatureSettings = "tnum"
    }
    private val dash = DashPathEffect(floatArrayOf(ui.dp(3).toFloat(), ui.dp(4).toFloat()), 0f)
    private val path = Path()
    private val area = Path()
    private val clock = DateTimeFormatter.ofPattern("HH:mm", Locale.getDefault()).withZone(ZoneId.systemDefault())
    private val day = DateTimeFormatter.ofPattern("dd MMM", Locale.getDefault()).withZone(ZoneId.systemDefault())
    private var reveal = 1f
    private var selected: Int? = null
    private val plot = RectF()
    private var segmentPoints: List<List<PointF>> = emptyList()

    init {
        importantForAccessibility = if (compact) IMPORTANT_FOR_ACCESSIBILITY_NO else IMPORTANT_FOR_ACCESSIBILITY_YES
        if (!compact && samples.size > 1 && ValueAnimator.areAnimatorsEnabled()) {
            reveal = 0f
            ValueAnimator.ofFloat(0f, 1f).apply {
                duration = 450; addUpdateListener { reveal = it.animatedValue as Float; invalidate() }
            }.start()
        }
    }

    private fun x(index: Int): Float {
        if (samples.size < 2) return plot.centerX()
        val first = samples.first().at.toEpochMilli(); val span = samples.last().at.toEpochMilli() - first
        return plot.left + if (span == 0L) plot.width() * index / (samples.size - 1)
            else ((samples[index].at.toEpochMilli() - first).toFloat() / span * plot.width())
    }
    private fun y(value: Double): Float {
        val low = ticks.first(); val high = ticks.last()
        return plot.bottom - ((value - low) / (high - low)).toFloat() * plot.height()
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        if (compact) plot.set(ui.dp(3).toFloat(), ui.dp(4).toFloat(), w - ui.dp(5).toFloat(), h - ui.dp(4).toFloat())
        else {
            val axisWidth = ticks.maxOfOrNull { label.measureText(metric.format(it)) } ?: 0f
            plot.set(ui.dp(6).toFloat(), ui.dp(14).toFloat(), w - axisWidth - ui.dp(12), h - ui.dp(24).toFloat())
        }
        val green = ui.color(R.color.prominent_top)
        fill.shader = LinearGradient(0f, plot.top, 0f, plot.bottom,
            ui.withAlpha(green, if (ui.night) 0x55 else 0x44), ui.withAlpha(green, 0), Shader.TileMode.CLAMP)
        line.shader = LinearGradient(plot.left, 0f, plot.right, 0f, ui.water, green, Shader.TileMode.CLAMP)
        var offset = 0
        segmentPoints = segments.map { segment ->
            segment.indices.map { PointF(x(offset + it), y(segment[it].value)) }.also { offset += segment.size }
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (samples.isEmpty()) return
        val green = ui.color(R.color.prominent_top)
        if (!compact) drawAxes(canvas)
        canvas.save()
        canvas.clipRect(0f, 0f, plot.left + (plot.width() + ui.dp(12)) * reveal, height.toFloat())
        for (points in segmentPoints) {
            if (points.size > 1) {
                path.reset(); area.reset()
                points.forEachIndexed { i, p -> if (i == 0) path.moveTo(p.x, p.y) else path.lineTo(p.x, p.y) }
                area.addPath(path); area.lineTo(points.last().x, plot.bottom); area.lineTo(points.first().x, plot.bottom); area.close()
                canvas.drawPath(area, fill)
                canvas.drawPath(path, line)
            }
            // Point marks show each reception; an isolated reception is still visible.
            if (!compact || points.size == 1) points.forEach { p ->
                paint.style = Paint.Style.FILL; paint.color = ui.color(R.color.surface)
                canvas.drawCircle(p.x, p.y, ui.dp(3).toFloat(), paint)
                paint.style = Paint.Style.STROKE; paint.strokeWidth = ui.dp(2).toFloat(); paint.color = green
                canvas.drawCircle(p.x, p.y, ui.dp(3).toFloat(), paint)
            }
        }
        canvas.restore()
        val focus = selected ?: samples.lastIndex
        val fx = x(focus); val fy = y(samples[focus].value)
        if (reveal >= 1f) {
            paint.style = Paint.Style.FILL
            paint.color = ui.withAlpha(green, 0x40); canvas.drawCircle(fx, fy, ui.dp(if (compact) 6 else 9).toFloat(), paint)
            paint.color = green; canvas.drawCircle(fx, fy, ui.dp(if (compact) 3 else 5).toFloat(), paint)
            paint.color = Color.WHITE; canvas.drawCircle(fx, fy, ui.dp(if (compact) 1 else 2).toFloat(), paint)
        }
        if (selected != null) {
            paint.style = Paint.Style.STROKE; paint.strokeWidth = ui.dp(1).toFloat(); paint.color = ui.withAlpha(ui.ink, 0x80)
            canvas.drawLine(fx, plot.top - ui.dp(8), fx, plot.bottom, paint)
        }
    }

    private fun drawAxes(canvas: Canvas) {
        paint.style = Paint.Style.STROKE; paint.strokeWidth = ui.dp(1).toFloat()
        paint.color = ui.withAlpha(ui.color(R.color.sky_deep), if (ui.night) 0x55 else 0x30)
        label.textAlign = Paint.Align.LEFT
        ticks.forEach { tick ->
            val ty = y(tick)
            canvas.drawLine(plot.left, ty, plot.right, ty, paint)
            canvas.drawText(metric.format(tick), plot.right + ui.dp(8), ty + label.textSize / 3, label)
        }
        // Average rule: a reference computed from these readings, not a target.
        if (samples.size > 1) {
            paint.pathEffect = dash; paint.color = ui.withAlpha(ui.water, 0xAA)
            val ay = y(average); canvas.drawLine(plot.left, ay, plot.right, ay, paint); paint.pathEffect = null
        }
        val baseline = height - ui.dp(6).toFloat()
        val first = samples.first().at; val last = samples.last().at
        val sameDay = day.format(first) == day.format(last)
        label.textAlign = Paint.Align.LEFT
        canvas.drawText(if (sameDay) clock.format(first) else "${day.format(first)} ${clock.format(first)}", plot.left, baseline, label)
        if (samples.size > 1) {
            label.textAlign = Paint.Align.RIGHT
            canvas.drawText(if (sameDay) clock.format(last) else "${day.format(last)} ${clock.format(last)}", plot.right, baseline, label)
        }
        label.textAlign = Paint.Align.LEFT
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (compact || samples.size < 2) return super.onTouchEvent(event)
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN, MotionEvent.ACTION_MOVE -> {
                parent?.requestDisallowInterceptTouchEvent(true)
                val nearest = samples.indices.minBy { kotlin.math.abs(x(it) - event.x) }
                if (nearest != selected) { selected = nearest; onInspect(samples[nearest]); invalidate() }
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                selected = null; onInspect(null); invalidate()
                if (event.actionMasked == MotionEvent.ACTION_UP) performClick()
            }
        }
        return true
    }
    override fun performClick(): Boolean = super.performClick()
}
