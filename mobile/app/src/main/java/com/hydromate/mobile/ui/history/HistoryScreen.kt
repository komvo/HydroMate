package com.hydromate.mobile.ui.history

import android.app.AlertDialog
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import com.hydromate.mobile.Measurement
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.*
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

val Metric.symbol get() = when (this) {
    Metric.PH -> GlassSymbol.CHEMISTRY
    Metric.TEMPERATURE -> GlassSymbol.THERMOMETER
    Metric.LIGHT -> GlassSymbol.SUN
    else -> GlassSymbol.TDS
}

// The app is Spanish-only and builds its copy inline, like every other screen.
@android.annotation.SuppressLint("SetTextI18n")
class HistoryScreen(private val ui: Components) {
    private val clock = DateTimeFormatter.ofPattern("HH:mm", Locale.getDefault()).withZone(ZoneId.systemDefault())
    private val day = DateTimeFormatter.ofPattern("EEEE dd MMM yyyy", Locale.getDefault()).withZone(ZoneId.systemDefault())

    fun render(root: LinearLayout, state: ReadingState, selected: Metric, select: (Metric) -> Unit,
               refresh: () -> Unit, settings: () -> Unit) = with(ui) {
        portalHeader(root, "Historial", "Tu torre en el tiempo", GlassSymbol.HISTORY)
        val values = (state as? ReadingState.Ready)?.values.orEmpty()
        if (values.isEmpty()) {
            val empty = card(root)
            empty.gravity = Gravity.CENTER_HORIZONTAL
            empty.addView(icon(GlassSymbol.HISTORY, 64))
            empty.addView(text(when (state) {
                is ReadingState.Loading -> if (state.requested) "Solicitando medición al ESP32…" else "Actualizando historial…"
                is ReadingState.Failed -> "No podemos actualizar las lecturas"
                else -> "Aún no hay lecturas"
            }, 20, true).apply { gravity = Gravity.CENTER })
            empty.addView(text(if (state is ReadingState.Failed) "Vuelve a intentarlo o revisa la conexión en Más."
                else "Aquí aparecerán las recepciones de esta torre.", 16, tint = muted).apply { gravity = Gravity.CENTER })
            actions(empty, button("Reintentar", refresh).apply { isEnabled = state !is ReadingState.Loading },
                button("Conexión", settings, false))
            return@with
        }
        root.addView(onBackdrop(text("Últimas ${values.size} lecturas recibidas", 14, tint = backdropMuted)))
        val metrics = Metric.entries.filter { it != Metric.EC || values.any { row -> row.ecUsCm != null } }
        segmented(root, metrics.map { it.title }, metrics.indexOf(selected), if (largeText) 2 else metrics.size,
            { index, active -> "Mostrar ${metrics[index].title}${if (active) ", seleccionado" else ""}" }) { select(metrics[it]) }

        val unit = selected.unitFor(values)
        val samples = TrendMath.samples(values, selected)
        val hero = card(root)
        val title = row()
        title.addView(iconWell(selected.symbol, 26))
        title.addView(text(if (unit.isEmpty()) selected.title else "${selected.title} · $unit", 16, true, muted),
            LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(10) })
        hero.addView(title)
        if (samples.isEmpty()) {
            hero.addView(text("—", 40, true).apply { setPadding(0, dp(8), 0, 0) })
            hero.addView(text("${selected.title} sin lecturas disponibles. No se sustituyen por cero.", 14, tint = muted))
        } else {
            // Headline readout: the newest value, or the inspected point while dragging.
            val readout = metric(selected.format(samples.last().value), unit, 40).apply { setPadding(0, dp(8), 0, 0) }
            val when_ = text("", 13, tint = muted)
            fun showLatest() {
                readout.text = metric(selected.format(samples.last().value), unit, 40).text
                when_.text = "Última lectura · ${relativeTime(samples.last().at)}"
            }
            showLatest()
            hero.addView(readout); hero.addView(when_)
            TrendMath.change(samples, selected, unit)?.let { hero.addView(text(it, 16, true).apply {
                setPadding(0, dp(6), 0, dp(2)); accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
            }) }
            if (selected == Metric.TDS && values.any { it.tdsSimulated }) hero.addView(badge("Incluye TDS simulado"))
            val chart = TrendChart(context, samples, selected, ui = ui) { sample ->
                if (sample == null) showLatest() else {
                    readout.text = metric(selected.format(sample.value), unit, 40).text
                    when_.text = "${day.format(sample.at)} · ${clock.format(sample.at)}"
                }
            }
            val segments = TrendMath.segments(samples)
            chart.contentDescription = "Gráfica de ${selected.title}: ${samples.size} lecturas, de ${selected.format(samples.minOf { it.value })} a " +
                "${selected.format(samples.maxOf { it.value })} $unit. ${TrendMath.change(samples, selected, unit) ?: "Una sola lectura"}. Los valores están en la tabla de recepciones."
            hero.addView(chart, LinearLayout.LayoutParams(-1, dp(if (largeText) 240 else 210)).apply { topMargin = dp(10) })
            if (samples.size > 1) hero.addView(text("┅ Promedio de estas lecturas: ${selected.format(samples.map { it.value }.average())} $unit".trimEnd(),
                12, true, water).apply { setPadding(0, dp(6), 0, 0) })
            hero.addView(text(when {
                samples.size == 1 -> "Una lectura; aún no hay tendencia."
                segments.size > 1 -> "Toca y desliza para ver cada lectura. La línea se corta donde faltan recepciones."
                else -> "Toca y desliza para ver cada lectura."
            }, 12, tint = muted).apply { setPadding(0, dp(6), 0, 0) })
            if (samples.size != values.size) hero.addView(text(
                if (selected == Metric.LIGHT) "Solo se grafican registros en $unit." else "${values.size - samples.size} recepciones sin ${selected.title}; no se sustituyen por cero.",
                12, tint = muted))

            // Summary statistics computed from these readings only; they are not targets.
            val stats = row().apply { gravity = Gravity.TOP }
            root.addView(stats, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
            listOf("Mínimo" to samples.minOf { it.value }, "Promedio" to samples.map { it.value }.average(),
                "Máximo" to samples.maxOf { it.value }).forEachIndexed { index, (name, value) ->
                val tile = surface().apply { setPadding(dp(12), dp(10), dp(12), dp(12)) }
                tile.addView(text(name, 12, true, muted))
                tile.addView(metric(selected.format(value), if (unit.length <= 3) unit else "", 20).apply { setPadding(0, dp(2), 0, 0) })
                stats.addView(tile, LinearLayout.LayoutParams(0, -2, 1f).apply { if (index > 0) marginStart = dp(8) })
            }
        }
        val about = card(root)
        about.addView(text("Qué mide", 15, true))
        about.addView(text(selected.about, 14, tint = muted))
        if (selected == Metric.TDS && values.any { it.tdsUsesReferenceTemperature })
            about.addView(text("Algunas lecturas usan la referencia de 25 °C porque faltó la temperatura.", 13, tint = muted))

        section(root, "Recepciones", "Más reciente primero · toca una fila para ver el detalle")
        if (values.all { it.synthetic }) root.addView(badge("Datos de prueba en todas las filas", fill = color(R.color.warning_soft)).apply {
            (layoutParams as LinearLayout.LayoutParams).marginStart = dp(4)
        })
        val table = group(root)
        val columns = metrics
        fun header(m: Metric) = when (m) { Metric.PH -> "pH"; Metric.TEMPERATURE -> "°C"; Metric.TDS -> "ppm"
            Metric.LIGHT -> if (Metric.LIGHT.unitFor(values) == "lux") "lux" else "%"; Metric.EC -> "µS" }
        if (!largeText) {
            val head = row().apply { setPadding(0, dp(10), 0, dp(6)) }
            head.addView(text("Hora", 12, true, muted), LinearLayout.LayoutParams(0, -2, 1.2f))
            columns.forEach { m -> head.addView(text(header(m), 12, true, if (m == selected) primary else muted).apply { gravity = Gravity.END },
                LinearLayout.LayoutParams(0, -2, 1f)) }
            table.addView(head)
        }
        var lastDay = ""
        values.forEach { m ->
            val dayLabel = day.format(m.received)
            if (dayLabel != lastDay) {
                lastDay = dayLabel
                if (table.childCount > 0) divider(table)
                table.addView(text(dayLabel.replaceFirstChar { it.titlecase(Locale.getDefault()) }, 12, true, primary).apply { setPadding(0, dp(10), 0, dp(4)) })
            } else divider(table)
            val line = if (largeText) column() else row()
            line.setPadding(0, dp(10), 0, dp(10)); line.minimumHeight = dp(48)
            fun cell(metric: Metric): String {
                val value = metric.read(m) ?: return "—"
                return metric.format(value) + if (metric == Metric.TDS && m.tdsSimulated) "*" else ""
            }
            if (largeText) {
                line.addView(text(clock.format(m.received), 16, true))
                line.addView(text(columns.joinToString(" · ") { "${cell(it)} ${header(it)}" }, 15).apply { fontFeatureSettings = "tnum" })
            } else {
                line.addView(text(clock.format(m.received), 14, true).apply { fontFeatureSettings = "tnum" }, LinearLayout.LayoutParams(0, -2, 1.2f))
                columns.forEach { metric ->
                    line.addView(text(cell(metric), 14, metric == selected, if (metric == selected) ink else muted).apply {
                        gravity = Gravity.END; fontFeatureSettings = "tnum"; maxLines = 1
                    }, LinearLayout.LayoutParams(0, -2, 1f))
                }
            }
            line.isClickable = true; line.isFocusable = true
            line.background = android.graphics.drawable.StateListDrawable().apply {
                addState(intArrayOf(android.R.attr.state_pressed), background(withAlpha(color(R.color.selected), 0x88), 12))
                addState(intArrayOf(android.R.attr.state_focused), background(withAlpha(color(R.color.selected), 0x88), 12))
                addState(intArrayOf(), background(android.graphics.Color.TRANSPARENT))
            }
            line.contentDescription = "${date(m.received)}. " + columns.joinToString(". ") { "${it.title} ${cell(it)}" } + ". Abrir detalle."
            line.setOnClickListener { detail(m) }
            table.addView(line, LinearLayout.LayoutParams(-1, -2))
        }
        if (values.any { it.tdsSimulated }) root.addView(text("* TDS simulado", 12, tint = backdropMuted).apply { onBackdrop(this); setPadding(dp(4), dp(6), 0, 0) })
    }

    private fun detail(m: Measurement) = with(ui) {
        fun show(value: Double?, metric: Metric, unit: String) = value?.let { "${metric.format(it)} $unit".trim() } ?: "Sin lectura"
        val lines = buildList {
            add("Recibido: ${date(m.received)}")
            m.captured?.let { add("Captura en el equipo: ${date(it)}") }
            add("Secuencia: ${m.sequence}")
            add("")
            add("pH: ${show(m.ph, Metric.PH, "")}")
            add("Temperatura: ${show(m.temperature, Metric.TEMPERATURE, "°C")}")
            add("TDS: ${show(m.tds, Metric.TDS, "ppm")}${if (m.tdsSimulated) " (simulado)" else ""}${if (m.tdsUsesReferenceTemperature) " · ref. 25 °C" else ""}")
            m.ecUsCm?.let { add("EC: ${show(it, Metric.EC, "µS/cm")}") }
            add("Luz: ${show(m.lightValue, Metric.LIGHT, m.lightUnit)}")
            add("Agua: ${m.waterDescription}")
            if (m.sources.isNotEmpty()) { add(""); add("Origen: " + m.sources.entries.joinToString(", ") { "${it.key} ${it.value}" }) }
            if (m.synthetic) { add(""); add("Datos de prueba.") }
        }
        AlertDialog.Builder(context).setTitle("Lectura ${clock.format(m.received)}")
            .setMessage(lines.joinToString("\n")).setPositiveButton("Cerrar", null).show()
    }
}
