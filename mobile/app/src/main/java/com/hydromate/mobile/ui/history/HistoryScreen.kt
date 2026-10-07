package com.hydromate.mobile.ui.history

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RadialGradient
import android.graphics.Shader
import android.view.View
import android.widget.LinearLayout
import com.hydromate.mobile.Measurement
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.*

enum class Metric(val title: String, val unit: String, val read: (Measurement) -> Double) {
    PH("pH", "", { it.ph }), TEMPERATURE("Temp.", "°C", { it.temperature }),
    TDS("TDS", "ppm", { it.tds }), LIGHT("Luz", "% relativo", { it.light })
}

class HistoryScreen(private val ui: Components) {
    fun render(root: LinearLayout, state: ReadingState, selected: Metric, select: (Metric) -> Unit,
               refresh: () -> Unit, settings: () -> Unit) = with(ui) {
        portalHeader(root, "Historial", "Tu torre en el tiempo", GlassSymbol.HISTORY)
        root.addView(text("Últimas 20 lecturas · por recepción", 14, tint = backdropMuted))
        val values = (state as? ReadingState.Ready)?.values.orEmpty()
        if (values.isEmpty()) {
            val empty = card(root)
            empty.addView(icon(GlassSymbol.HISTORY, 52))
            empty.addView(text(when (state) {
                is ReadingState.Loading -> "Actualizando historial…"
                is ReadingState.Failed -> "No podemos actualizar las lecturas"
                else -> "Aún no hay lecturas"
            }, 20, true))
            empty.addView(text(if (state is ReadingState.Failed) "Vuelve a intentarlo o revisa la conexión en Más."
                else "Aquí aparecerán las recepciones de esta torre.", 16, tint = muted))
            actions(empty, button("Reintentar", refresh).apply { isEnabled = state !is ReadingState.Loading },
                button("Conexión", settings, false))
            return@with
        }
        val plotCard = card(root)
        plotCard.addView(badge("Registro reciente", fill = color(R.color.sky)))
        Metric.entries.chunked(if (largeText) 2 else 4).forEach { group ->
            val selector = row()
            plotCard.addView(selector, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(8) })
            group.forEachIndexed { index, metric ->
                selector.addView(button(metric.title, { select(metric) }, metric == selected).apply {
                    setPadding(dp(4), dp(8), dp(4), dp(8))
                    isSelected = metric == selected
                    contentDescription = "Mostrar ${metric.title}${if (isSelected) ", seleccionado" else ""}"
                }, LinearLayout.LayoutParams(0, -2, 1f).apply { if (index > 0) marginStart = dp(4) })
            }
        }
        plotCard.addView(text(listOf(selected.title, selected.unit).filter { it.isNotEmpty() }.joinToString(" · "), 20, true))
        plotCard.addView(TrendView(context, values, selected, ui), LinearLayout.LayoutParams(-1, dp(if (largeText) 200 else 156)))
        val ordered = values.sortedBy { it.received }
        plotCard.addView(text("Desde ${date(ordered.first().received)}\nHasta ${date(ordered.last().received)}", 12, tint = muted))
        val numbers = values.map(selected.read)
        plotCard.addView(text("Mín. ${number(numbers.min())} · Máx. ${number(numbers.max())} ${selected.unit}", 14, tint = muted))
        plotCard.addView(text(if (values.size == 1) "Una lectura; aún no hay tendencia."
            else "Cada punto es una recepción. No se asume continuidad entre lecturas.", 14, tint = muted))
        section(root, "Recepciones", "${values.size} registros · más reciente primero")
        values.forEach { m ->
            val entry = card(root)
            entry.addView(text(date(m.received), 16, true))
            if (m.synthetic) entry.addView(badge("Datos de prueba"))
            entry.addView(text("pH ${number(m.ph)} · Temperatura ${number(m.temperature)} °C\nTDS ${number(m.tds)} ppm", 16))
            entry.addView(text("Luz relativa ${number(m.light)} % · ${m.lightState}\nNivel relativo ${number(m.water)} % · ${m.waterState}", 14, tint = muted))
        }
    }
}

private class TrendView @JvmOverloads constructor(context: Context, rows: List<Measurement> = emptyList(),
                        private val metric: Metric = Metric.PH, private val ui: Components = Components(context)) : View(context) {
    private val points = rows.sortedBy { it.received }
    private val numbers = points.map(metric.read)
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val pointRadius = ui.dp(5).toFloat()
    private val pearl = RadialGradient(-pointRadius * .3f, -pointRadius * .35f, pointRadius * 1.4f,
        intArrayOf(0xFFE8FCFF.toInt(), ui.color(R.color.aqua), ui.water),
        floatArrayOf(0f, .3f, 1f), Shader.TileMode.CLAMP)
    init {
        contentDescription = "Gráfica de ${metric.title}, ${rows.size} puntos por hora de recepción. Los valores están disponibles en la lista de historial."
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES
    }
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (points.isEmpty()) return
        val margin = ui.dp(12).toFloat()
        val w = width - 2 * margin
        val h = height - 2 * margin
        val min = numbers.min(); val max = numbers.max()
        val start = points.first().received.toEpochMilli()
        val duration = points.last().received.toEpochMilli() - start
        fun x(index: Int) = margin + if (duration == 0L) w / 2 else ((points[index].received.toEpochMilli() - start).toDouble() / duration * w).toFloat()
        fun y(index: Int) = margin + if (max == min) h / 2 else (h * (1 - (numbers[index] - min) / (max - min))).toFloat()
        paint.color = ui.color(R.color.outline); paint.strokeWidth = ui.dp(1).toFloat()
        paint.alpha = 110
        for (i in 0..2) canvas.drawLine(margin, margin + h * i / 2, width - margin, margin + h * i / 2, paint)
        paint.alpha = 255
        paint.color = ui.water
        // Samples are isolated; the API reports no sampling cadence or continuity.
        for (i in points.indices) {
            canvas.save(); canvas.translate(x(i), y(i))
            paint.shader = pearl
            canvas.drawCircle(0f, 0f, pointRadius, paint)
            paint.shader = null; paint.color = ui.water; paint.style = Paint.Style.STROKE
            paint.strokeWidth = resources.displayMetrics.density * .6f
            canvas.drawCircle(0f, 0f, pointRadius, paint)
            paint.style = Paint.Style.FILL
            canvas.restore()
        }
    }
}
