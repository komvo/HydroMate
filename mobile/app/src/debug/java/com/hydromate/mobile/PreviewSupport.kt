package com.hydromate.mobile

import com.hydromate.mobile.ui.*
import java.time.Instant

/** Debug-only deterministic fixtures. No HTTP, MQTT, storage or hardware access. */
object PreviewSupport {
    val options = listOf("Conexión real", "Lecturas de ejemplo", "Carga", "Vacío", "Error de conexión",
        "Lectura antigua", "Sensor ausente (rechazo v1)", "Una sola lectura")
    private val received = Instant.parse("2026-09-01T12:00:00Z")
    private val checked = Instant.parse("2026-10-03T18:00:00Z")
    fun referenceAge(index: Int, configured: Int) = if (index == 5) 30 else configured
    fun load(index: Int): ReadingState? = when (index) {
        0 -> null
        2 -> ReadingState.Loading
        3 -> ReadingState.Empty(checked)
        4 -> ReadingState.Failed(FailureKind.NETWORK, "Escenario de demostración: conexión no disponible.")
        6 -> runCatching { Telemetry.parse("""[{"device_id":"test-demo-aero","sequence":1,"created_at":"2026-09-01T12:00:00Z","temperature_c":23,"ph":null,"tds_ppm":510,"light_pct":60,"light_state":"MEDIA","water_level_pct":65,"water_level_state":"MEDIO"}]""", "test-demo-aero") }
            .fold({ error("El contrato v1 debe rechazar un sensor ausente") }, { failure(it) })
        else -> ReadingState.Ready(List(if (index == 7) 1 else 20) { i ->
            Measurement(20L - i, "test-demo-aero", received.minusSeconds(i * 240L),
                23.0 + (i % 4) * .2, 6.1 + (i % 3) * .04, 510.0 + i * 2,
                60.0 + i % 5, "MEDIA", 65.0, "MEDIO", true)
        }, checked)
    }
}
