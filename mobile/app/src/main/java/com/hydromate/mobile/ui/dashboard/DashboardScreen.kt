package com.hydromate.mobile.ui.dashboard

import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.ProgressBar
import com.hydromate.mobile.R
import com.hydromate.mobile.TelemetryState
import com.hydromate.mobile.ui.*
import com.hydromate.mobile.ui.history.Metric
import com.hydromate.mobile.ui.history.TrendChart
import com.hydromate.mobile.ui.history.TrendMath
import com.hydromate.mobile.ui.history.symbol
import java.time.Instant

class DashboardScreen(private val ui: Components) {
    fun render(root: LinearLayout, state: ReadingState, name: String, ageMinutes: Int,
               refresh: () -> Unit, settings: () -> Unit,
               cultivation: () -> Unit, equipment: () -> Unit, history: (Metric) -> Unit = {}) = with(ui) {
        val heading = row().apply { setPadding(0, dp(8), 0, dp(2)) }
        val identity = column()
        identity.addView(onBackdrop(text("HydroMate", titleSize(34), true, backdropInk)).apply {
            if (android.os.Build.VERSION.SDK_INT >= 28) isAccessibilityHeading = true
        })
        if (!largeText) identity.addView(onBackdrop(text("Agua, vida y tecnología", 15, tint = backdropMuted)))
        heading.addView(identity, LinearLayout.LayoutParams(0, -2, 1f))
        heading.addView(iconButton(R.drawable.aero_refresh, "Solicitar medición nueva", refresh).apply {
            isEnabled = state !is ReadingState.Loading
            alpha = if (isEnabled) 1f else .45f
        }, LinearLayout.LayoutParams(dp(52), dp(52)))
        root.addView(heading)

        // Hero: the original botanical emblem on a tinted green glass panel.
        val hero = card(root, color(R.color.glass))
        hero.setPadding(dp(14), dp(12), dp(16), dp(12))
        val heroRow = row()
        if (!largeText) heroRow.addView(icon(GlassSymbol.CULTIVATION, 92))
        val copy = column()
        copy.addView(text(name, if (largeText) 17 else 20, true))
        if (!largeText) copy.addView(text("Tu espacio para crecer", 14, true, primary))
        copy.addView(badge(if (largeText) "Sin perfil" else "Sin perfil de cultivo", fill = color(R.color.lime)))
        copy.addView(text("Ver cultivo ›", 13, true, primary).apply { setPadding(dp(2), dp(6), 0, 0) })
        heroRow.addView(copy, LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(10) })
        hero.addView(heroRow)
        hero.isClickable = true; hero.isFocusable = true
        pressable(hero)
        hero.contentDescription = "$name. Sin perfil de cultivo. Emblema decorativo sin estado físico. Abrir Cultivo."
        hero.setOnClickListener { cultivation() }

        val readings = (state as? ReadingState.Ready)?.values.orEmpty()
        val latest = readings.firstOrNull()
        val previous = readings.getOrNull(1)
        val old = (state as? ReadingState.Ready)?.deviceState == TelemetryState.STALE || latest?.let { isOld(it.captured ?: it.received, Instant.now(), ageMinutes) } == true
        val failed = state is ReadingState.Failed
        val hasActions = failed || state is ReadingState.Empty
        val status = surface(if (failed || old) color(R.color.warning_soft) else null, if (hasActions) 26 else CAPSULE)
        status.setPadding(dp(16), dp(10), dp(16), dp(10))
        root.addView(status, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) })
        val message = when (state) {
            is ReadingState.Failed -> "No podemos actualizar las lecturas"
            is ReadingState.Loading -> if (state.requested) "Solicitando medición al ESP32…" else "Actualizando lecturas…"
            is ReadingState.Empty -> "Sin lecturas para esta torre"
            is ReadingState.Ready -> "${if (old) "Sin datos recientes · última" else "Última"} lectura ${latest?.let { relativeTime(it.received) }.orEmpty()}"
            else -> "Consulta las lecturas de tu torre"
        }
        val tone = if (state is ReadingState.Failed && state.kind == FailureKind.INVALID) color(R.color.critical)
            else if (failed || old) color(R.color.warning) else ink
        val statusLine = row()
        // Activity is shown as motion, not only text; the dot only mirrors the text tone.
        statusLine.addView(if (state is ReadingState.Loading) ProgressBar(context, null, android.R.attr.progressBarStyleSmall).apply {
            indeterminateTintList = android.content.res.ColorStateList.valueOf(primary)
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        } else View(context).apply {
            background = GradientDrawable().apply { shape = GradientDrawable.OVAL; setColor(if (failed || old) tone else primary) }
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }, if (state is ReadingState.Loading) LinearLayout.LayoutParams(dp(18), dp(18)) else LinearLayout.LayoutParams(dp(8), dp(8)))
        val statusCopy = column()
        statusCopy.addView(text(message, 14, true, tone).apply { accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE })
        when (state) {
            is ReadingState.Ready -> latest?.let { statusCopy.addView(text("Recibida ${date(it.received)}", 12, tint = muted)) }
            is ReadingState.Failed -> statusCopy.addView(text(state.kind.explanation, 12, tint = muted))
            is ReadingState.Loading -> if (state.requested) statusCopy.addView(text("El equipo mide y envía la lectura; puede tardar unos segundos.", 12, tint = muted))
            else -> Unit
        }
        statusLine.addView(statusCopy, LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(10) })
        status.addView(statusLine)
        if (hasActions) actions(status, button("Reintentar", refresh), button("Conexión", settings, false))

        // One context note instead of repeating "no range" in every instrument.
        section(root, "Lecturas", "Sin rangos de cultivo: los valores no se califican. Toca una lectura para ver su historial.")
        val metrics = listOf(Metric.PH, Metric.TEMPERATURE, Metric.TDS, Metric.LIGHT) +
            if (latest?.ecUsCm != null) listOf(Metric.EC) else emptyList()
        metrics.chunked(if (twoColumns) 2 else 1).forEach { group ->
            val line = row().apply { gravity = Gravity.TOP }
            root.addView(line, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
            group.forEachIndexed { index, metric ->
                val value = latest?.let(metric.read)
                val unit = metric.unitFor(readings)
                val label = if (metric == Metric.TDS && latest?.tdsSimulated == true) "TDS simulado" else metric.title
                val longUnit = unit.contains(' ')
                val instrument = surface()
                instrument.setPadding(dp(14), dp(12), dp(14), dp(12))
                line.addView(instrument, LinearLayout.LayoutParams(0, -1, 1f).apply { if (index > 0) marginStart = dp(10) })
                val title = row()
                title.addView(iconWell(metric.symbol, 26))
                title.addView(text(label, 14, true, muted),
                    LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(8) })
                title.addView(text("›", 20, tint = muted).apply { importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO })
                instrument.addView(title)
                instrument.addView(metric(value?.let(metric::format) ?: "—", if (longUnit) "" else unit).apply { setPadding(dp(2), dp(6), 0, 0) })
                // Multi-word units sit under the value so neither the label nor the number wraps.
                if (longUnit) instrument.addView(text(unit, 12, true, muted).apply { setPadding(dp(2), 0, 0, 0) })
                val samples = TrendMath.samples(readings, metric)
                if (samples.size > 1) instrument.addView(TrendChart(context, samples, metric, compact = true, ui = ui),
                    LinearLayout.LayoutParams(-1, dp(30)).apply { topMargin = dp(2) })
                val footnote = when {
                    value == null -> if (metric == Metric.TDS) "TDS no disponible" else "Sin lectura"
                    old -> "Lectura antigua"
                    metric == Metric.TDS && latest?.tdsUsesReferenceTemperature == true -> "Sin compensación térmica · ref. 25 °C"
                    else -> TrendMath.step(previous?.let(metric.read), value, metric, unit) ?: "Sin lectura anterior para comparar"
                }
                instrument.addView(text(footnote, 12, tint = muted).apply { setPadding(dp(2), dp(2), 0, 0) })
                instrument.isClickable = true; instrument.isFocusable = true
                pressable(instrument)
                instrument.contentDescription = "${if (metric == Metric.TEMPERATURE) "Temperatura de la solución" else label}: " +
                    "${value?.let { "${metric.format(it)} $unit" } ?: "sin lectura"}. $footnote. Abrir historial."
                instrument.setOnClickListener { history(metric) }
            }
        }
        val waterCard = card(root, color(R.color.water_soft))
        val waterRow = row()
        waterRow.addView(icon(GlassSymbol.DROPLET, 56))
        val waterCopy = column()
        waterCopy.addView(text(if (latest != null && (latest.version >= 2 || latest.waterPresent != null)) "Flotador · nivel discreto" else "Nivel relativo · prototipo", 14, true, muted))
        waterCopy.addView(text(latest?.waterDescription ?: "—", 22, true))
        waterCopy.addView(text(if (latest == null) "Sin lectura" else if (old) "Lectura antigua" else if (latest.waterPresent != null) "Indica presencia de agua, no litros" else "Porcentaje relativo del prototipo, no litros", 12, tint = muted))
        waterRow.addView(waterCopy, LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(12) })
        waterCard.addView(waterRow)

        section(root, "Entender HydroMate")
        val learn = group(root)
        listRow(learn, GlassSymbol.IRRIGATION, "Cómo llegan tus datos", "De la torre a este teléfono") {
            help("Cómo llegan tus datos", "1. La torre (ESP32) mide pH, temperatura, TDS, luz y nivel de agua.\n\n" +
                "2. Envía cada lectura cifrada al servidor de HydroMate cuando hay un cambio significativo y, como respaldo, cada 30 s.\n\n" +
                "3. El servidor la guarda. Mientras ves Inicio o Historial, esta app consulta las últimas lecturas cada 2 s.\n\n" +
                "Solicitar medición (botón ⟳ o deslizar hacia abajo) pide al equipo una lectura nueva. Si no responde a tiempo, la app lo indica y conserva las lecturas anteriores.\n\n" +
                "La hora mostrada es la de recepción en el servidor. Una respuesta del servidor no confirma por sí sola que el equipo esté conectado.")
        }
        listRow(learn, GlassSymbol.CHEMISTRY, "Qué mide cada sensor", "pH, temperatura, TDS, luz y agua") {
            help("Qué mide cada sensor", Metric.entries.filter { it != Metric.EC || latest?.ecUsCm != null }
                .joinToString("\n\n") { "${it.title}: ${it.about}" } +
                "\n\nAgua: un flotador indica si hay agua en el depósito (lecturas v2 o superiores); los registros v1 muestran un porcentaje relativo." +
                "\n\nHydroMate todavía no tiene rangos por cultivo, así que muestra los valores sin calificarlos.")
        }
        section(root, "Equipo y control")
        listRow(group(root), GlassSymbol.CONTROL, "Ver equipo y control", "Integración pendiente", equipment)
    }
}
