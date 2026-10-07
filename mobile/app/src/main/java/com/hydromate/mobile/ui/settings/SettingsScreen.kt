package com.hydromate.mobile.ui.settings

import android.app.AlertDialog
import android.text.InputType
import android.view.View
import android.widget.*
import com.hydromate.mobile.PreviewSupport
import com.hydromate.mobile.R
import com.hydromate.mobile.Telemetry
import com.hydromate.mobile.ui.*

data class ConnectionSettings(val server: String, val device: String, val name: String, val ageMinutes: Int) {
    fun draft() = ConnectionDraft(server, device, name, ageMinutes.toString())
}
data class ConnectionDraft(val server: String, val device: String, val name: String, val age: String) {
    fun validated(): ConnectionSettings {
        val url = server.trim().trimEnd('/')
        val tower = device.trim()
        Telemetry.endpoint(url, tower)
        require(name.trim().isNotEmpty() && name.trim().length <= 64) { "El nombre debe tener entre 1 y 64 caracteres." }
        val minutes = age.toIntOrNull()
        require(minutes != null && minutes in 0..10080) { "La referencia debe ser un entero entre 0 y 10080 minutos." }
        return ConnectionSettings(url, tower, name.trim(), minutes)
    }
}

class SettingsScreen(private val ui: Components) {
    private var server: EditText? = null
    private var device: EditText? = null
    private var name: EditText? = null
    private var age: EditText? = null
    private var diagnostic: LinearLayout? = null
    private var connectionStatus: TextView? = null
    var advanced = false
    var diagnostics = false

    fun draft(): ConnectionDraft? = server?.let {
        ConnectionDraft(it.text.toString(), device!!.text.toString(), name!!.text.toString(), age!!.text.toString())
    }

    fun render(root: LinearLayout, config: ConnectionDraft, state: ReadingState, save: () -> Unit,
               equipment: () -> Unit, appearance: String, changeAppearance: (String) -> Unit,
               scenario: Int, changeScenario: (Int) -> Unit, saved: List<ConnectionSettings>,
               chooseTower: (ConnectionSettings) -> Unit) = with(ui) {
        portalHeader(root, "Tu HydroMate", "Centro de conexión y preferencias", GlassSymbol.SETTINGS)
        section(root, "Torre")
        val tower = card(root)
        fun field(parent: LinearLayout, title: String, value: String, id: Int,
                  type: Int = InputType.TYPE_CLASS_TEXT): EditText {
            val label = text(title, 14, true).apply { labelFor = id }
            parent.addView(label)
            return EditText(context).apply {
                this.id = id; inputType = type; setSingleLine(true); setText(value); setTextColor(ink)
                contentDescription = title; minHeight = dp(52)
                background = AeroSurface(ui, color(R.color.surface), radius = 10)
                backgroundTintList = null
                setPadding(dp(8), dp(8), dp(8), dp(8))
                parent.addView(this, LinearLayout.LayoutParams(-1, -2))
            }
        }
        name = field(tower, "Nombre en este teléfono", config.name, 101)
        tower.addView(button("Equipo y control", equipment, false))
        if (saved.size > 1) tower.addView(button("Elegir torre guardada", {
            AlertDialog.Builder(context).setTitle("Torres en este teléfono")
                .setItems(saved.map { "${it.name} · ${it.device}" }.toTypedArray()) { _, index -> chooseTower(saved[index]) }
                .setNegativeButton("Cancelar", null).show()
        }, false))
        section(root, "Conexión")
        val connection = card(root)
        connectionStatus = text("", 14, true).also { connection.addView(it) }
        disclosure(connection, "conexión avanzada", advanced, { advanced = it }) { form ->
            device = field(form, "Identificador de torre (device_id)", config.device, 102)
            server = field(form, "Servidor · dirección base sin /api", config.server, 103,
                InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI)
            age = field(form, "Lectura antigua · referencia en minutos", config.age, 104, InputType.TYPE_CLASS_NUMBER)
            form.addView(text("0 desactiva la referencia. Es una ayuda visual, no un indicador de conexión del ESP32.", 14, tint = muted))
            disclosure(form, "guía USB, emulador y Wi-Fi") { guide ->
                guide.addView(text("USB: 127.0.0.1:8000 con el enlace ADB preparado en la PC.\nEmulador Android: 10.0.2.2:8000.\nWi-Fi: requiere un servidor accesible en esa red.\nHTTP solo en debug; release requiere HTTPS.", 14, tint = muted))
            }
        }
        connection.addView(button(if (scenario > 0) "Guardar conexión real" else "Guardar y probar conexión", save))
        disclosure(connection, "diagnóstico", diagnostics, { diagnostics = it }) { detail -> diagnostic = detail }
        updateState(state, scenario > 0)

        section(root, "Apariencia")
        val design = card(root)
        design.addView(text("Aero Eco · Jardín de cristal", 20, true))
        design.addView(text("Hojas, agua y cristal verde. Elige paneles claros o la apariencia de tu teléfono.", 14, tint = muted))
        design.addView(button(if (appearance == "aero") "Seguir tema del sistema" else "Usar Jardín claro", {
            changeAppearance(if (appearance == "aero") "system" else "aero")
        }, false))
        design.addView(text("Movimiento breve al navegar; se respeta la desactivación de animaciones de Android.", 14, tint = muted))

        if (PreviewSupport.options.isNotEmpty()) {
            section(root, "Demostración · solo debug")
            val demo = card(root)
            demo.addView(text("Escenarios locales sin conexión al equipo. No se activan al fallar el servidor.", 14, tint = muted))
            demo.addView(button(if (scenario > 0) "Escenario: ${PreviewSupport.options[scenario]}" else "Elegir demostración", {
                AlertDialog.Builder(context).setTitle("Demostración · datos simulados")
                    .setSingleChoiceItems(PreviewSupport.options.toTypedArray(), scenario) { dialog, which ->
                        dialog.dismiss(); changeScenario(which)
                    }.setNegativeButton("Cancelar", null).show()
            }, false))
            if (scenario > 0) demo.addView(button("Salir de la demostración", { changeScenario(0) }))
        }

        section(root, "Créditos")
        val credits = card(root)
        credits.addView(icon(GlassSymbol.CULTIVATION, 60))
        credits.addView(text("Emblema, iconos y fondo vegetal originales generados con IA para HydroMate.\nSuperficies de cristal: gráficos nativos propios.\nTipografía: sans-serif del sistema.", 14, tint = muted))
        credits.addView(button("Acerca del diseño", {
            help("HydroMate · Aero Eco", "Inspirado en el optimismo ecológico de Frutiger Aero y los portales de internet clásicos.\n\nEl emblema es decorativo: no representa volumen, plantas activas ni estado físico. El cristal se dibuja por capas; no refracta contenido en tiempo real.\n\nLas referencias visuales, procedencia y avisos están en la documentación del proyecto.")
        }, false))
        credits.addView(text("HydroMate 0.6.0 · Jardín de cristal", 12, tint = muted))
    }

    fun updateState(state: ReadingState, demonstration: Boolean) = with(ui) {
        connectionStatus?.text = if (demonstration) "Fuente de demostración · sin consultar servidor" else when (state) {
            is ReadingState.Ready, is ReadingState.Empty -> "Servidor disponible en la última consulta"
            is ReadingState.Loading -> "Consultando servidor…"
            is ReadingState.Failed -> "No podemos actualizar las lecturas"
            else -> "Conexión sin comprobar"
        }
        diagnostic?.let { detail ->
            detail.removeAllViews()
            detail.addView(text("Comunicación ESP32 y sensores físicos: no verificados.", 14, tint = muted))
            when (state) {
                is ReadingState.Ready -> {
                    detail.addView(text("${if (demonstration) "Consulta simulada" else "Última consulta"} · ${date(state.checked)}", 14))
                    state.values.firstOrNull()?.let {
                        detail.addView(text("Recibido · ${date(it.received)}\nSecuencia · ${it.sequence}\nTorre · ${it.device}", 14, tint = muted))
                    }
                }
                is ReadingState.Empty -> detail.addView(text("Consulta · ${date(state.checked)}\nSin registros; no confirma existencia de la torre.", 14, tint = muted))
                is ReadingState.Failed -> {
                    detail.addView(text(state.kind.explanation, 14))
                    detail.addView(text("Detalle · ${state.detail}", 14, tint = muted))
                }
                else -> Unit
            }
        }
    }
}
