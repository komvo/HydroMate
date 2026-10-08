package com.hydromate.mobile

import org.junit.Assert.*
import org.junit.Test

class TelemetryTest {
    private val v2 = """[{"message_version":2,"device_id":"hydromate-01","sequence":1,"created_at":"2026-10-07T19:00:00Z","temperature_c":24.3,"ph":6.2,"tds_ppm":650,"light_lux":450.5,"water_present":false,"sources":{"temperature_c":"real","ph":"real","light_lux":"real","water_present":"real","tds_ppm":"simulated"}}]"""
    @Test fun parsesPhysicalUnitsAndMarksOnlyTdsSimulated() {
        val m = Telemetry.parse(v2, "hydromate-01").single()
        assertEquals(450.5, m.lightValue, 0.001)
        assertEquals("lux", m.lightUnit)
        assertEquals(false, m.waterPresent)
        assertEquals("Nivel bajo / sin agua", m.waterDescription)
        assertTrue(m.tdsSimulated)
        assertFalse(m.synthetic)
        assertNull(m.light)
    }
    @Test fun rejectsV2WithoutProvenanceAndWithNumericFloatSwitch() {
        assertThrows(IllegalArgumentException::class.java) { Telemetry.parse(v2.replace("\"message_version\":2", "\"message_version\":\"2\""), "hydromate-01") }
        assertThrows(RuntimeException::class.java) { Telemetry.parse(v2.replace("\"tds_ppm\":\"simulated\"", "\"tds_ppm\":\"unknown\""), "hydromate-01") }
        assertThrows(IllegalArgumentException::class.java) { Telemetry.parse(v2.replace("\"water_present\":false", "\"water_present\":0"), "hydromate-01") }
    }
    private val body = """[{"device_id":"test-01","sequence":3000000000,"created_at":"2026-09-30T19:00:00.000000Z","temperature_c":24.3,"ph":6.2,"tds_ppm":650,"light_pct":65.2,"light_state":"MEDIA","water_level_pct":82.4,"water_level_state":"LLENO","reason":["synthetic_test"]}]"""

    @Test fun parsesContractNumbersAndServerTimestamp() {
        val reading = Telemetry.parse(body, "test-01").single()
        assertEquals(3000000000L, reading.sequence)
        assertEquals(650.0, reading.tds, 0.001)
        assertEquals("2026-09-30T19:00:00Z", reading.received.toString())
        assertTrue(reading.synthetic)
    }
    @Test fun emptyHistoryDoesNotInventMeasurements() {
        assertTrue(Telemetry.parse("[]", "tower").isEmpty())
    }
    @Test(expected = IllegalArgumentException::class) fun rejectsMixedDevices() {
        Telemetry.parse(body, "another-tower")
    }
    @Test fun encodesDeviceQuery() {
        val url = Telemetry.endpoint("http://127.0.0.1:8000/", "tower&limit=100")
        assertTrue(url.contains("device_id=tower%26limit%3D100&limit=20"))
    }
    @Test fun rejectsMalformedBaseUrls() {
        listOf("file:///tmp/data", "http://host/api", "http://user:secret@host", "http://host?q=1", "http://host#fragment").forEach {
            assertThrows(IllegalArgumentException::class.java) { Telemetry.endpoint(it, "tower") }
        }
    }
    @Test fun rejectsMissingSensorRatherThanShowingZero() {
        assertThrows(org.json.JSONException::class.java) { Telemetry.parse(body.replace("\"ph\":6.2", "\"ph\":null"), "test-01") }
    }
    @Test fun liveDeviceDoesNotAcquireSyntheticLabel() {
        assertFalse(Telemetry.parse(body.replace("test-01", "hydromate-01").replace("synthetic_test", "startup"), "hydromate-01").single().synthetic)
    }
    @Test fun rejectsContractViolationsAndInvalidReceptionDates() {
        listOf(body.replace("\"ph\":6.2", "\"ph\":50"),
            body.replace("\"sequence\":3000000000", "\"sequence\":1.5"),
            body.replace("MEDIA", "UNKNOWN"),
            body.replace("2026-09-30T19:00:00.000000Z", "yesterday")).forEach { malformed ->
            assertThrows(RuntimeException::class.java) { Telemetry.parse(malformed, "test-01") }
        }
    }
    @Test fun rejectsTheWholeResponseIfOneRowHasMissingData() {
        val complete = body.removePrefix("[").removeSuffix("]")
        val partial = complete.replace("\"ph\":6.2", "\"ph\":null")
        assertThrows(org.json.JSONException::class.java) { Telemetry.parse("[$complete,$partial]", "test-01") }
    }
}
