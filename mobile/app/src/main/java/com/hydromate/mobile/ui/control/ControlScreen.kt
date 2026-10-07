package com.hydromate.mobile.ui.control

import android.widget.LinearLayout
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.*

class ControlScreen(private val ui: Components) {
    fun render(root: LinearLayout, back: () -> Unit, expanded: Boolean, expand: (Boolean) -> Unit) = with(ui) {
        portalHeader(root, "Control", "Automatización con cuidado", GlassSymbol.CONTROL)
        val panel = card(root)
        panel.addView(badge("Integración pendiente"))
        panel.addView(text("Esperando al dispositivo", 22, true))
        panel.addView(text("Aquí verás el equipo cuando HydroMate reciba estados y confirmaciones reales.", 15, tint = muted))
        fun module(symbol: GlassSymbol, title: String, detail: String) {
            val line = row().apply { setPadding(0, dp(12), 0, dp(12)) }
            line.addView(icon(symbol, 40))
            val copy = column()
            copy.addView(text(title, 16, true)); copy.addView(text(detail, 14, tint = muted))
            line.addView(copy, LinearLayout.LayoutParams(0, -2, 1f).apply { marginStart = dp(10) })
            panel.addView(line)
        }
        module(GlassSymbol.IRRIGATION, "Circuito de agua", "Recirculación · bomba principal")
        module(GlassSymbol.SUN, "Luz para crecer", "Iluminación")
        module(GlassSymbol.CHEMISTRY, "Dosificación", "Nutriente A · Nutriente B\npH Up · pH Down")
        panel.addView(text("Sin estados reportados · sin acciones habilitadas", 13, true, muted))
        disclosure(panel, "detalles de integración", expanded, expand) { detail ->
            detail.addView(text("Aún no se reciben estados ni confirmaciones de ejecución. No hay controles manuales habilitados.", 14, tint = muted))
            detail.addView(text("Los canales químicos no presuponen un mecanismo de dosificación. El esquema no confirma válvulas cerradas, bombas detenidas ni circulación.", 14, tint = muted))
            detail.addView(text("Las protecciones críticas se ejecutarán localmente en el ESP32. Su implementación y validación física siguen pendientes.", 14, tint = muted))
        }
        root.addView(button("Volver", back, false).apply {
            layoutParams = LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) }
        })
    }
}
