package com.hydromate.mobile

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URLEncoder
import java.time.Instant
import java.time.Duration

data class Measurement(
    val sequence: Long, val device: String, val received: Instant,
    val temperature: Double?, val ph: Double?, val tds: Double?,
    val light: Double?, val lightState: String, val water: Double?,
    val waterState: String, val synthetic: Boolean,
    val lightLux: Double? = null, val waterPresent: Boolean? = null,
    val sources: Map<String, String> = emptyMap(),
    val ecUsCm: Double? = null, val captured: Instant? = null, val version: Int = 1
) {
    val tdsSimulated: Boolean get() = sources["tds_ppm"] == "simulated"
    val tdsUsesReferenceTemperature: Boolean get() = version == 3 && tds != null &&
        sources["tds_ppm"] == "real" && temperature == null
    val lightValue: Double? get() = lightLux ?: light
    val lightUnit: String get() = if (version >= 2 || lightLux != null) "lux" else "% relativo"
    val waterDescription: String get() = waterPresent?.let { if (it) "Agua detectada" else "Nivel bajo / sin agua" }
        ?: if (version >= 2) "Flotador sin lectura" else "$water % relativo · $waterState"
}

enum class TelemetryState { NO_DATA, RECENT, STALE }
data class TelemetrySnapshot(val readings: List<Measurement>, val freshnessSeconds: Int,
    val deviceState: TelemetryState)

fun telemetryState(values: List<Measurement>, now: Instant, thresholdSeconds: Int = 120): TelemetryState {
    val latest = values.firstOrNull() ?: return TelemetryState.NO_DATA
    val age = maxOf(Duration.between(latest.received, now).seconds,
        Duration.between(latest.captured ?: latest.received, now).seconds)
    return if (age > thresholdSeconds) TelemetryState.STALE else TelemetryState.RECENT
}

object Telemetry {
    fun endpoint(base: String, device: String, production: Boolean = false): String {
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
        require(!production || uri.scheme == "https") { "Producción requiere una URL HTTPS pública, sin /api." }
        require(!production || !device.startsWith("test-")) { "Producción requiere la identidad real de la torre." }
        return "${uri.toASCIIString().trimEnd('/')}/api/measurements?device_id=${URLEncoder.encode(device, "UTF-8")}&limit=20${if (production) "&real_only=1" else ""}"
    }

    fun parse(body: String, device: String, production: Boolean = false): List<Measurement> {
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
            val version = if (item.isNull("message_version")) 1 else {
                require(item.get("message_version") in listOf(2, 3)) { "Versión de telemetría no compatible." }
                item.getInt("message_version")
            }
            if (version >= 2) {
                val sourceObject = item.getJSONObject("sources")
                val keys = listOf("temperature_c", "light_lux", "water_present", "ph", "tds_ppm") + if (version == 3) listOf("ec_us_cm") else emptyList()
                require(sourceObject.length() == keys.size) { "Origen de sensores incompleto." }
                val sources = keys.associateWith { key -> sourceObject.getString(key).also {
                    require(it in (if (version == 3) listOf("real", "simulated", "unavailable", "invalid") else listOf("real", "simulated"))) { "Origen inválido en $key" }
                } }
                fun sensor(key: String, range: ClosedFloatingPointRange<Double>): Double? {
                    require(item.has(key)) { "Falta sensor $key" }
                    val absent = item.isNull(key)
                    if (version == 3) {
                        require(absent == (sources[key] in listOf("unavailable", "invalid"))) { "Origen y valor no coinciden en $key" }
                        if (absent) return null
                        require(item.get(key) is Number) { "$key requiere número JSON" }
                    }
                    return number(key, range)
                }
                require(item.has("water_present")) { "Falta flotador" }
                val water = if (item.isNull("water_present")) null else item.get("water_present")
                if (version == 3) require((water == null) == (sources["water_present"] in listOf("unavailable", "invalid"))) { "Origen del flotador no coincide." }
                require((version == 3 && water == null) || water is Boolean) { "El flotador requiere un booleano JSON." }
                require(!production || (!synthetic && sources.values.none { it == "simulated" })) { "Producción recibió datos de prueba; no se mostrarán como reales." }
                return@map Measurement(sequence, device, Instant.parse(item.getString("created_at")),
                    sensor("temperature_c", 0.0..50.0), sensor("ph", 0.0..14.0), sensor("tds_ppm", 0.0..1000.0),
                    null, "", null, "", synthetic,
                    sensor("light_lux", 0.0..100000.0), water as Boolean?, sources,
                    if (version == 3) sensor("ec_us_cm", 0.0..100000.0) else null,
                    if (item.isNull("captured_at")) null else Instant.parse(item.getString("captured_at")), version)
            }
            require(!production) { "Producción requiere telemetría con origen explícito (v2/v3)." }
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
class AcquisitionTimeoutException : java.io.IOException("El ESP32 no confirmó una medición nueva a tiempo.")
class AcquisitionUnavailableException : java.io.IOException("La API todavía no admite solicitudes de medición para esta torre.")

class TelemetryRepository {
    fun load(endpoint: String, device: String): List<Measurement> = loadSnapshot(endpoint, device).readings

    fun requestFreshSnapshot(endpoint: String, device: String, production: Boolean = false,
                             timeoutMs: Long = 35_000, pollMs: Long = 500): TelemetrySnapshot {
        require(!production || URI(endpoint).scheme == "https") { "Producción requiere HTTPS." }
        val address = apiPath(endpoint, "/devices/$device/measurement-requests")
        val created = try { exchange(address, "POST", 202) }
            catch (error: TelemetryHttpException) {
                if (error.status in listOf(403, 404)) throw AcquisitionUnavailableException()
                throw error
            }
        val id = created.getString("id")
        require(java.util.UUID.fromString(id).toString() == id.lowercase()) { "Identificador de solicitud inválido." }
        require(created.getString("device_id") == device) { "Solicitud de otra torre." }
        val notBefore = Instant.parse(created.getString("created_at")).truncatedTo(java.time.temporal.ChronoUnit.SECONDS)
        val deadline = System.nanoTime() + timeoutMs * 1_000_000
        while (System.nanoTime() < deadline) {
            if (Thread.currentThread().isInterrupted) throw InterruptedException()
            val result = try { exchange(apiPath(endpoint, "/measurement-requests/$id"), "GET", 200) }
                catch (error: TelemetryHttpException) {
                    if (error.status == 404) throw AcquisitionTimeoutException()
                    throw error
                }
            require(result.getString("id") == id && result.getString("device_id") == device)
            when (result.getString("state")) {
                "stored" -> {
                    val item = result.getJSONObject("measurement")
                    val reasons = item.getJSONArray("reason")
                    require((0 until reasons.length()).any { reasons.getString(it) == "request:$id" })
                    val acquired = Telemetry.parse(JSONArray().put(item).toString(), device, production).single()
                    require(acquired.captured != null && !acquired.captured.isBefore(notBefore)) {
                        "La respuesta no corresponde a una adquisición nueva."
                    }
                    val snapshot = loadSnapshot(endpoint, device, production)
                    val rows = (snapshot.readings + acquired).distinctBy { it.sequence }.sortedByDescending { it.received }.take(20)
                    return snapshot.copy(readings = rows, deviceState = telemetryState(rows, Instant.now(), snapshot.freshnessSeconds))
                }
                "expired" -> throw AcquisitionTimeoutException()
                "pending" -> Thread.sleep(pollMs)
                else -> throw IllegalArgumentException("Estado de solicitud desconocido.")
            }
        }
        throw AcquisitionTimeoutException()
    }

    private fun apiPath(endpoint: String, suffix: String): String {
        val uri = URI(endpoint)
        require(uri.path.endsWith("/measurements")) { "Endpoint de mediciones inválido." }
        return URI(uri.scheme, null, uri.host, uri.port, uri.path.removeSuffix("/measurements") + suffix, null, null).toString()
    }

    private fun exchange(address: String, method: String, expected: Int): JSONObject {
        val connection = URI(address).toURL().openConnection() as HttpURLConnection
        try {
            connection.connectTimeout = 8000; connection.readTimeout = 8000
            connection.instanceFollowRedirects = false
            connection.useCaches = false
            connection.requestMethod = method
            connection.setRequestProperty("Accept", "application/json")
            if (method == "POST") {
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.setFixedLengthStreamingMode(2)
                connection.outputStream.use { it.write("{}".toByteArray(Charsets.UTF_8)) }
            }
            val status = connection.responseCode
            if (status != expected) throw TelemetryHttpException(status)
            val body = connection.inputStream.bufferedReader(Charsets.UTF_8).use { reader ->
                val text = StringBuilder(); val buffer = CharArray(4096)
                while (true) {
                    val count = reader.read(buffer)
                    if (count < 0) break
                    require(text.length + count <= 1_000_000) { "Respuesta demasiado grande." }
                    text.append(buffer, 0, count)
                }
                text.toString()
            }
            return JSONObject(body)
        } finally { connection.disconnect() }
    }

    fun loadSnapshot(endpoint: String, device: String, production: Boolean = false): TelemetrySnapshot {
        require(!production || URI(endpoint).scheme == "https") { "Producción requiere HTTPS." }
        val connection = URI(endpoint).toURL().openConnection() as HttpURLConnection
        try {
            connection.connectTimeout = 8000
            connection.readTimeout = 8000
            connection.instanceFollowRedirects = false
            connection.useCaches = false
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
            val values = Telemetry.parse(body, device, production)
            val freshness = connection.getHeaderField("X-HydroMate-Freshness-Seconds")?.toIntOrNull()?.takeIf { it in 1..86400 } ?: 120
            return TelemetrySnapshot(values, freshness, telemetryState(values, Instant.now(), freshness))
        } finally {
            connection.disconnect()
        }
    }
}
