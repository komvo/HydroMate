package com.hydromate.mobile.ui.cultivation

import android.widget.LinearLayout
import com.hydromate.mobile.R
import com.hydromate.mobile.ui.*

class CultivationScreen(private val ui: Components) {
    fun render(root: LinearLayout) = with(ui) {
        portalHeader(root, "Cultivo", "Crecer con intención", GlassSymbol.CULTIVATION)
        val empty = card(root, color(R.color.lime))
        empty.addView(text("Espacio para crecer", 24, true, primary))
        empty.addView(text("Tu cultivo tendrá aquí su propio perfil.", 16))
        empty.addView(badge("Sin perfil vinculado", fill = color(R.color.lime)))
        empty.addView(text("Cuando el servicio de perfiles esté disponible, podrás vincular uno a tu torre.", 14, tint = muted))
        section(empty, "Cada planta, su contexto", inSurface = true)
        empty.addView(text("Etapa, objetivos y rangos del cultivo siguen pendientes. Por ahora mostramos las lecturas sin calificarlas como óptimas.", 14, tint = muted))
        empty.addView(button("Sobre los perfiles", {
            help("Un perfil para tu cultivo", "El perfil relacionará una planta y su etapa con objetivos del entorno. Todavía no existe un servicio de perfiles integrado; no hay cultivo activo, receta validada ni rangos configurados.")
        }, false))
    }
}
