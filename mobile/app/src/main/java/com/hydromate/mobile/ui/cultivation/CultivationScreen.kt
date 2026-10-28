package com.hydromate.mobile.ui.cultivation

import android.view.Gravity
import android.widget.LinearLayout
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.*

class CultivationScreen(private val ui: Components) {
    fun render(root: LinearLayout) = with(ui) {
        portalHeader(root, "Cultivo", "Crecer con intención", GlassSymbol.CULTIVATION)
        val empty = card(root, color(R.color.glass))
        empty.gravity = Gravity.CENTER_HORIZONTAL
        empty.setPadding(dp(18), dp(18), dp(18), dp(18))
        empty.addView(icon(GlassSymbol.CULTIVATION, if (largeText) 96 else 140))
        empty.addView(text("Espacio para crecer", 24, true, primary).apply { gravity = Gravity.CENTER })
        empty.addView(text("Tu cultivo tendrá aquí su propio perfil.", 16).apply { gravity = Gravity.CENTER })
        empty.addView(badge("Sin perfil vinculado", fill = color(R.color.lime)).apply {
            (layoutParams as LinearLayout.LayoutParams).apply { gravity = Gravity.CENTER_HORIZONTAL; topMargin = dp(10) }
        })
        empty.addView(text("Cuando el servicio de perfiles esté disponible, podrás vincular uno a tu torre.", 14, tint = muted).apply {
            gravity = Gravity.CENTER; setPadding(0, dp(10), 0, 0)
        })
        section(root, "Cada planta, su contexto")
        val context = card(root)
        context.addView(text("Etapa, objetivos y rangos del cultivo siguen pendientes. Por ahora mostramos las lecturas sin calificarlas como óptimas.", 14, tint = muted))
        context.addView(button("Sobre los perfiles", {
            help("Un perfil para tu cultivo", "El perfil relacionará una planta y su etapa con objetivos del entorno. Todavía no existe un servicio de perfiles integrado; no hay cultivo activo, receta validada ni rangos configurados.")
        }, false), LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) })
    }
}
