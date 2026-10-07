package com.hydromate.mobile.ui

import com.hydromate.mobile.Measurement
import com.hydromate.mobile.TelemetryHttpException
import java.io.IOException
import java.net.SocketTimeoutException
import java.time.Duration
import java.time.Instant

enum class Destination(val title: String, val icon: GlassSymbol) {
    HOME("Inicio", GlassSymbol.HOME),
    HISTORY("Historial", GlassSymbol.HISTORY),
    CULTIVATION("Cultivo", GlassSymbol.CULTIVATION),
    CONTROL("Control", GlassSymbol.CONTROL),
    SETTINGS("Más", GlassSymbol.SETTINGS)
}

enum class FailureKind(val title: String, val explanation: String) {
    TIMEOUT("El servidor está tardando", "La consulta no terminó a tiempo. Puedes volver a intentarlo."),
    NETWORK("No pudimos acceder al servidor", "Revisa el servidor y la conexión USB o Wi-Fi del teléfono."),
    INVALID("No pudimos interpretar las lecturas", "La respuesta está incompleta o no coincide con esta torre. No mostramos valores dudosos."),
    AUTH("El servidor requiere autorización", "Esta versión no tiene acceso autenticado. Revisa la configuración del servidor."),
    PARAMETERS("Revisa la conexión configurada", "El servidor rechazó los parámetros de consulta."),
    SERVER("El servicio no está disponible", "El servidor respondió con un error. Vuelve a intentarlo más tarde."),
    ADDRESS("Revisa la dirección del servidor", "Introduce una dirección base y una torre válidas en Ajustes.")
}

sealed class ReadingState {
    data object Idle : ReadingState()
    data object Loading : ReadingState()
    data class Empty(val checked: Instant) : ReadingState()
    data class Ready(val values: List<Measurement>, val checked: Instant) : ReadingState()
    data class Failed(val kind: FailureKind, val detail: String) : ReadingState()
}

fun failure(error: Throwable): ReadingState.Failed {
    val kind = when (error) {
        is SocketTimeoutException -> FailureKind.TIMEOUT
        is TelemetryHttpException -> when (error.status) {
            401, 403 -> FailureKind.AUTH
            422 -> FailureKind.PARAMETERS
            else -> FailureKind.SERVER
        }
        is IOException -> FailureKind.NETWORK
        else -> FailureKind.INVALID
    }
    return ReadingState.Failed(kind, error.message ?: error.javaClass.simpleName)
}

// This is a user-selected display threshold, never an ESP32 heartbeat or crop limit.
fun isOld(received: Instant, now: Instant, ageMinutes: Int): Boolean =
    ageMinutes > 0 && Duration.between(received, now) >= Duration.ofMinutes(ageMinutes.toLong())

fun relativeTime(instant: Instant, now: Instant = Instant.now()): String {
    val seconds = Duration.between(instant, now).seconds
    return when {
        seconds < 0 -> "fecha adelantada; revisa el reloj del servidor"
        seconds < 60 -> "hace unos segundos"
        seconds < 3600 -> "hace ${seconds / 60} min"
        seconds < 86400 -> "hace ${seconds / 3600} h"
        else -> "hace ${seconds / 86400} días"
    }
}
