package com.hydromate.mobile

import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import java.time.Instant
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class AcquisitionTest {
    private val id = "12345678-1234-1234-1234-123456789abc"
    private fun measurement(reason: String): JSONObject = JSONObject().apply {
        put("device_id", "hydromate-01"); put("message_version", 3); put("sequence", 2)
        put("created_at", Instant.now().toString()); put("captured_at", Instant.now().toString())
        put("reason", JSONArray().put(reason))
        put("temperature_c", JSONObject.NULL); put("ph", 6.2); put("tds_ppm", 500.0)
        put("light_lux", 150.0); put("water_present", true); put("ec_us_cm", JSONObject.NULL)
        put("sources", JSONObject().put("temperature_c", "invalid").put("ph", "real").put("tds_ppm", "real")
            .put("light_lux", "real").put("water_present", "real").put("ec_us_cm", "unavailable"))
    }

    private fun exercise(state: String, matchingReason: Boolean = true): TelemetrySnapshot {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val item = measurement(if (matchingReason) "request:$id" else "periodic_poc")
        var polls = 0
        server.createContext("/api/") { exchange ->
            val path = exchange.requestURI.path
            val body: String
            val code: Int
            when {
                path.endsWith("/hydromate-01/measurement-requests") -> {
                    assertEquals("POST", exchange.requestMethod)
                    assertEquals("{}", exchange.requestBody.bufferedReader().readText())
                    code = 202
                    body = JSONObject().put("id", id).put("device_id", "hydromate-01")
                        .put("created_at", Instant.now().minusSeconds(1).toString()).toString()
                }
                path.endsWith("/measurement-requests/$id") -> {
                    code = 200; polls++
                    body = JSONObject().put("id", id).put("device_id", "hydromate-01")
                        .put("state", if (polls == 1) "pending" else state).put("measurement", item).toString()
                }
                else -> { code = 200; body = JSONArray().put(item).toString() }
            }
            val bytes = body.toByteArray(Charsets.UTF_8)
            exchange.sendResponseHeaders(code, bytes.size.toLong())
            exchange.responseBody.use { it.write(bytes) }
        }
        server.start()
        return try {
            val endpoint = Telemetry.endpoint("http://127.0.0.1:${server.address.port}", "hydromate-01")
            TelemetryRepository().requestFreshSnapshot(endpoint, "hydromate-01", timeoutMs = 3000, pollMs = 5)
        } finally { server.stop(0) }
    }

    @Test fun refreshWaitsForCorrelatedPhysicalSampleAndKeepsRealTdsWithoutPretendingTemperature() {
        val row = exercise("stored").readings.single()
        assertEquals(500.0, row.tds!!, 0.01)
        assertNull(row.temperature)
        assertTrue(row.tdsUsesReferenceTemperature)
    }

    @Test fun unrelatedPeriodicReadingCannotSatisfyRefresh() {
        assertThrows(IllegalArgumentException::class.java) { exercise("stored", matchingReason = false) }
    }

    @Test fun validMeasuredTemperatureKeepsTdsWithoutTheReferenceWarning() {
        val item = measurement("sensor_change").put("temperature_c", 24.5)
        item.getJSONObject("sources").put("temperature_c", "real")
        val row = Telemetry.parse(JSONArray().put(item).toString(), "hydromate-01", true).single()
        assertEquals(24.5, row.temperature!!, 0.01)
        assertEquals(500.0, row.tds!!, 0.01)
        assertFalse(row.tdsUsesReferenceTemperature)
    }

    @Test fun expiredRequestIsNotPresentedAsFreshData() {
        assertThrows(AcquisitionTimeoutException::class.java) { exercise("expired") }
    }
}
