package com.hydromate.mobile

import org.junit.Assert.*
import org.junit.Test
import java.time.Instant

class PartialTelemetryTest {
    private val body = """[{"message_version":3,"device_id":"hydromate-01","sequence":900,"created_at":"2026-10-14T19:00:00.000000Z","captured_at":"2026-10-14T18:55:00Z","temperature_c":24.3,"ph":null,"tds_ppm":null,"ec_us_cm":null,"light_lux":450.5,"water_present":false,"sources":{"temperature_c":"real","ph":"invalid","light_lux":"real","water_present":"real","tds_ppm":"unavailable","ec_us_cm":"unavailable"}}]"""
    @Test fun productionPreservesUnavailableSensorsAndFalseFloat() {
        val value = Telemetry.parse(body, "hydromate-01", true).single()
        assertNull(value.ph)
        assertNull(value.tds)
        assertNull(value.ecUsCm)
        assertEquals(false, value.waterPresent)
        assertEquals("Nivel bajo / sin agua", value.waterDescription)
        assertFalse(value.synthetic)
    }
    @Test fun acquisitionAgePreventsLateDeliveryFromAppearingRecent() {
        val values = Telemetry.parse(body, "hydromate-01", true)
        assertEquals(TelemetryState.STALE, telemetryState(values, Instant.parse("2026-10-14T19:00:01Z")))
        assertEquals(TelemetryState.NO_DATA, telemetryState(emptyList(), Instant.now()))
        val recent = values.map { it.copy(captured = it.received) }
        assertEquals(TelemetryState.RECENT, telemetryState(recent, Instant.parse("2026-10-14T19:01:00Z")))
    }
    @Test fun productionRejectsSimulationAndPlainHttp() {
        assertThrows(IllegalArgumentException::class.java) { Telemetry.parse(body.replace("\"temperature_c\":\"real\"", "\"temperature_c\":\"simulated\""), "hydromate-01", true) }
        assertThrows(IllegalArgumentException::class.java) { Telemetry.endpoint("http://example.org:8081", "hydromate-01", true) }
        assertTrue(Telemetry.endpoint("https://api.example.org", "hydromate-01", true).endsWith("&real_only=1"))
    }
    @Test fun rejectsMissingFieldsAndContradictorySources() {
        listOf(body.replace("\"ph\":\"invalid\"", "\"ph\":\"real\""), body.replace("\"ph\":null,", ""), body.replace("\"temperature_c\":24.3", "\"temperature_c\":\"24.3\"")).forEach {
            assertThrows(RuntimeException::class.java) { Telemetry.parse(it, "hydromate-01") }
        }
    }
    @Test fun ecIsIndependentOfTds() {
        val value = Telemetry.parse(body.replace("\"ec_us_cm\":null", "\"ec_us_cm\":1100.5").replace("\"ec_us_cm\":\"unavailable\"", "\"ec_us_cm\":\"real\""), "hydromate-01", true).single()
        assertEquals(1100.5, value.ecUsCm!!, 0.001)
        assertNull(value.tds)
    }
}
