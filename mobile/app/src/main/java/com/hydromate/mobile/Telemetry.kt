package com.hydromate.mobile

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URLEncoder
import java.time.Instant

data class Measurement(
    val sequence: Long, val device: String, val received: Instant,
    val temperature: Double, val ph: Double, val tds: Double,
    val light: Double, val lightState: String, val water: Double,
    val waterState: String, val synthetic: Boolean
)

object Telemetry {
    fun endpoint(base: String, device: String): String {
        require(device.isNotBlank() && device.length <= 64) { "Escribe un dispositivo de hasta 64 caracteres." }
        val uri = try { URI(base.trim().trimEnd('/')) } catch (_: Exception) {
            throw IllegalArgumentException("Dirección inválida. Usa http://servidor:8000")
        }
        require(uri.scheme in listOf("http", "https") && !uri.host.isNullOrBlank()
            && uri.rawUserInfo == null && uri.rawQuery == null && uri.rawFragment == null
            && (uri.path.isNullOrEmpty() || uri.path == "/")
            && (uri.port == -1 || uri.port in 1..65535)) {
            "Usa solo la dirección base, por ejemplo http://127.0.0.1:8000, sin /api."
        }
        return "${uri.toASCIIString().trimEnd('/')}/api/measurements?device_id=${URLEncoder.encode(device, "UTF-8")}&limit=20"
    }

    fun parse(body: String, device: String): List<Measurement> {
        val array = JSONArray(body)
        require(array.length() <= 20) { "La API excedió el límite de 20 lecturas solicitado." }
        return (0 until array.length()).map { index ->
            val item = array.getJSONObject(index)
            require(item.getString("device_id") == device) { "La API devolvió datos de otra torre." }
            val reasons = item.optJSONArray("reason") ?: JSONArray()
            val synthetic = device.startsWith("test-") || (0 until reasons.length()).any { reasons.optString(it) == "synthetic_test" }
            fun number(key: String, range: ClosedFloatingPointRange<Double>): Double = item.getDouble(key).also {
                require(it.isFinite() && it in range) { "Valor no válido en $key" }
            }
            val sequence = item.get("sequence").toString().toLongOrNull()
            require(sequence != null && sequence > 0) { "Secuencia no válida." }
            val lightState = item.getString("light_state")
            val waterState = item.getString("water_level_state")
            require(lightState in listOf("BAJA", "MEDIA", "ALTA") && waterState in listOf("VACIO", "MEDIO", "LLENO")) {
                "Estado de sensor no válido."
            }
            Measurement(sequence, device, Instant.parse(item.getString("created_at")),
                number("temperature_c", 0.0..50.0), number("ph", 0.0..14.0), number("tds_ppm", 0.0..1000.0),
                number("light_pct", 0.0..100.0), lightState, number("water_level_pct", 0.0..100.0), waterState, synthetic)
        }
    }
}

class TelemetryHttpException(val status: Int) : IllegalStateException("HTTP $status")

class TelemetryRepository {
    fun load(endpoint: String, device: String): List<Measurement> {
        val connection = URI(endpoint).toURL().openConnection() as HttpURLConnection
        try {
            connection.connectTimeout = 8000
            connection.readTimeout = 8000
            connection.instanceFollowRedirects = false
            connection.setRequestProperty("Accept", "application/json")
            val status = connection.responseCode
            if (status != 200) {
                throw TelemetryHttpException(status)
            }
            val body = connection.inputStream.bufferedReader(Charsets.UTF_8).use { reader ->
                val text = StringBuilder()
                val buffer = CharArray(4096)
                while (true) {
                    val count = reader.read(buffer)
                    if (count == -1) break
                    require(text.length + count <= 1_000_000) { "Respuesta demasiado grande." }
                    text.append(buffer, 0, count)
                }
                text.toString()
            }
            return Telemetry.parse(body, device)
        } finally {
            connection.disconnect()
        }
    }
}
