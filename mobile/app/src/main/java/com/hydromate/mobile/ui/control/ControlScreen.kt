package com.hydromate.mobile.ui.control

import android.widget.LinearLayout
import com.hydromate.mobile.ui.*

class ControlScreen(private val ui: Components) {
    fun render(root: LinearLayout, back: () -> Unit, expanded: Boolean, expand: (Boolean) -> Unit) = with(ui) {
        portalHeader(root, "Control", "Automatización con cuidado", GlassSymbol.CONTROL)
        val panel = card(root)
        panel.addView(badge("Integración pendiente"))
        panel.addView(text("Esperando al dispositivo", 22, true).apply { setPadding(0, dp(8), 0, dp(2)) })
        panel.addView(text("Aquí verás el equipo cuando HydroMate reciba estados y confirmaciones reales.", 15, tint = muted))
        section(root, "Módulos", "Sin estados reportados · sin acciones habilitadas")
        val modules = group(root)
        listRow(modules, GlassSymbol.IRRIGATION, "Circuito de agua", "Recirculación · bomba principal")
        listRow(modules, GlassSymbol.SUN, "Luz para crecer", "Iluminación")
        listRow(modules, GlassSymbol.CHEMISTRY, "Dosificación", "Nutriente A · Nutriente B\npH Up · pH Down")
        val notes = card(root)
        disclosure(notes, "detalles de integración", expanded, expand) { detail ->
            detail.addView(text("Aún no se reciben estados ni confirmaciones de ejecución. No hay controles manuales habilitados.", 14, tint = muted).apply { setPadding(dp(4), dp(10), dp(4), dp(2)) })
            detail.addView(text("Los canales químicos no presuponen un mecanismo de dosificación. El esquema no confirma válvulas cerradas, bombas detenidas ni circulación.", 14, tint = muted).apply { setPadding(dp(4), dp(6), dp(4), dp(2)) })
            detail.addView(text("Las protecciones críticas se ejecutarán localmente en el ESP32. Su implementación y validación física siguen pendientes.", 14, tint = muted).apply { setPadding(dp(4), dp(6), dp(4), dp(2)) })
        }
        root.addView(button("Volver", back, false).apply {
            layoutParams = LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(14) }
        })
    }
}
