package com.hydromate.mobile.ui.dashboard

import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.*
import java.time.Instant

class DashboardScreen(private val ui: Components) {
    fun render(root: LinearLayout, state: ReadingState, name: String, ageMinutes: Int,
               refresh: () -> Unit, settings: () -> Unit,
               cultivation: () -> Unit, equipment: () -> Unit) = with(ui) {
        val heading = row()
        val identity = column()
        identity.addView(text("HydroMate", if (largeText) 22 else 28, true, backdropInk))
        if (!largeText) identity.addView(text("Agua, vida y tecnología", 13, tint = backdropMuted))
        heading.addView(identity, LinearLayout.LayoutParams(0, -2, 1f))
        heading.addView(iconButton(R.drawable.aero_refresh, "Actualizar lecturas", refresh).apply {
            isEnabled = state !is ReadingState.Loading
            alpha = if (isEnabled) 1f else .45f
        }, LinearLayout.LayoutParams(dp(52), dp(52)))
        root.addView(heading)

        val hero = card(root, color(R.color.sky))
        hero.background = AeroSurface(ui, color(R.color.sky), true, 24)
        hero.setPadding(dp(12), dp(6), dp(12), dp(6))
        val heroRow = row()
        if (!largeText) heroRow.addView(icon(GlassSymbol.CULTIVATION, 94))
        val copy = column()
        copy.addView(text(name, if (largeText) 16 else 18, true))
        if (!largeText) copy.addView(text("Tu espacio para crecer", 14, tint = primary))
        copy.addView(text(if (largeText) "Sin perfil · Ver cultivo ›" else "Sin perfil de cultivo · Ver cultivo ›", 12, tint = muted))
        heroRow.addView(copy, LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(8) })
        hero.addView(heroRow)
        hero.isClickable = true; hero.isFocusable = true
        hero.contentDescription = "$name. Sin perfil de cultivo. Emblema decorativo sin estado físico. Abrir Cultivo."
        hero.setOnClickListener { cultivation() }

        val latest = (state as? ReadingState.Ready)?.values?.firstOrNull()
        val old = latest?.let { isOld(it.received, Instant.now(), ageMinutes) } == true
        val status = card(root, color(if (state is ReadingState.Failed || old) R.color.warning_soft else R.color.surface))
        status.setPadding(dp(12), dp(9), dp(12), dp(9))
        val message = when (state) {
            is ReadingState.Failed -> "No podemos actualizar las lecturas"
            is ReadingState.Loading -> "Actualizando lecturas…"
            is ReadingState.Empty -> "Sin lecturas para esta torre"
            is ReadingState.Ready -> "${if (old) "Lectura antigua · " else ""}Recibido ${latest?.let { date(it.received) }.orEmpty()}"
            else -> "Consulta las lecturas de tu torre"
        }
        status.addView(text(message, 13, state is ReadingState.Failed,
            if (state is ReadingState.Failed && state.kind == FailureKind.INVALID) color(R.color.critical)
            else if (state is ReadingState.Failed || old) color(R.color.warning) else muted).apply {
            accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
        })
        if (state is ReadingState.Failed || state is ReadingState.Empty) {
            actions(status, button("Reintentar", refresh), button("Conexión", settings, false))
        }
        // One connection notice; instruments never fabricate values or repeat failures.
        data class Instrument(val label: String, val value: Double?, val unit: String, val symbol: GlassSymbol)
        val items = listOf(
            Instrument("pH", latest?.ph, "", GlassSymbol.CHEMISTRY),
            Instrument("Temp.", latest?.temperature, "°C", GlassSymbol.THERMOMETER),
            Instrument(if (latest?.tdsSimulated == true) "TDS simulado" else "TDS", latest?.tds, "ppm", GlassSymbol.TDS),
            Instrument("Luz", latest?.lightValue, latest?.lightUnit ?: "lux", GlassSymbol.SUN))
        items.chunked(if (twoColumns) 2 else 1).forEach { group ->
            val line = row().apply { gravity = Gravity.TOP }
            root.addView(line, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) })
            group.forEachIndexed { index, item ->
                val instrument = surface()
                instrument.setPadding(dp(10), dp(8), dp(10), dp(10))
                line.addView(instrument, LinearLayout.LayoutParams(0, -2, 1f).apply {
                    if (index > 0) marginStart = dp(12)
                })
                val title = row()
                title.addView(icon(item.symbol, 34))
                title.addView(text(item.label + if (item.unit.isEmpty()) "" else " · ${item.unit}", 13, true),
                    LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(5) })
                title.contentDescription = if (item.label == "Temp.") "Temperatura de la solución, grados Celsius" else null
                instrument.addView(title)
                instrument.addView(text(item.value?.let(::number) ?: "—", 30, true).apply {
                    fontFeatureSettings = "tnum"; setPadding(dp(4), 0, 0, 0)
                })
                instrument.addView(text(when {
                    item.value == null -> "Sin lectura"
                    old -> "Lectura antigua"
                    else -> "Sin rango configurado"
                }, 12, tint = muted).apply { setPadding(dp(4), 0, 0, 0) })
            }
        }
        val waterCard = card(root, color(R.color.sky))
        val waterRow = row()
        waterRow.addView(icon(GlassSymbol.DROPLET, 54))
        val waterCopy = column()
        waterCopy.addView(text(if (latest?.waterPresent != null) "Flotador · nivel discreto" else "Nivel relativo · prototipo", 14, true))
        waterCopy.addView(text(latest?.waterDescription ?: "—", 20, true))
        waterCopy.addView(text(if (latest == null) "Sin lectura" else if (old) "Lectura antigua" else "Sin rango configurado", 12, tint = muted))
        waterRow.addView(waterCopy, LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(10) })
        waterCard.addView(waterRow)
        waterCard.addView(button("Sobre estas lecturas", {
            help("Lecturas del prototipo", "Las lecturas v2 muestran luz en lux y presencia de agua mediante flotador; no litros ni porcentaje de llenado. TDS simulado se identifica en su tarjeta. Los registros v1 conservan sus porcentajes relativos. La fecha es recepción en el servidor. Una respuesta de la API no confirma conexión del ESP32.")
        }, false))
        section(root, "Equipo y control", "Integración pendiente")
        root.addView(button("Ver equipo y control", equipment, false).apply {
            layoutParams = LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) }
        })
    }
}
