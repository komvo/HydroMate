package com.hydromate.mobile

import android.content.Context
import com.hydromate.mobile.ui.settings.ConnectionSettings

/** Names/age preferences belong to a server + tower; no telemetry is persisted. */
class ConnectionStore(context: Context) {
    private val active = context.getSharedPreferences("connection", Context.MODE_PRIVATE)
    private val towers = context.getSharedPreferences("tower_settings", Context.MODE_PRIVATE)
    fun current(): ConnectionSettings {
        val environment = if (!BuildConfig.DEBUG) ConnectionEnvironment.PRODUCTION else
            ConnectionEnvironment.entries.find { it.name == active.getString("environment", "DEVELOPMENT") }
                ?: ConnectionEnvironment.DEVELOPMENT
        return profile(environment)
    }
    fun profile(environment: ConnectionEnvironment): ConnectionSettings {
        val development = environment == ConnectionEnvironment.DEVELOPMENT
        val prefix = environment.name.lowercase()
        return ConnectionSettings(
            active.getString("$prefix.server", if (development) active.getString("server", "http://127.0.0.1:8000") else BuildConfig.PRODUCTION_API_URL)!!,
            active.getString("$prefix.device", if (development) active.getString("device", "hydromate-01") else "hydromate-01")!!,
            active.getString("$prefix.name", if (development) active.getString("name", "Torre principal") else "Torre principal")!!,
            active.getInt("$prefix.age_minutes", if (development) active.getInt("age_minutes", 2) else 2), environment)
    }
    fun save(config: ConnectionSettings) {
        val prefix = config.environment.name.lowercase()
        val editor = active.edit().putString("environment", config.environment.name)
            .putString("$prefix.server", config.server).putString("$prefix.device", config.device)
            .putString("$prefix.name", config.name).putInt("$prefix.age_minutes", config.ageMinutes)
        if (config.environment == ConnectionEnvironment.DEVELOPMENT) editor.putString("server", config.server)
            .putString("device", config.device).putString("name", config.name).putInt("age_minutes", config.ageMinutes)
        editor.apply()
        val key = java.security.MessageDigest.getInstance("SHA-256")
            .digest("${config.environment}\n${config.server}\n${config.device}".toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
        val keys = towers.getStringSet("keys", emptySet())!!.toMutableSet().apply { add(key) }
        towers.edit().putStringSet("keys", keys).putString("$key.environment", config.environment.name).putString("$key.server", config.server)
            .putString("$key.device", config.device).putString("$key.name", config.name)
            .putInt("$key.age", config.ageMinutes).apply()
    }
    fun saved(): List<ConnectionSettings> = towers.getStringSet("keys", emptySet())!!.map { key ->
        ConnectionSettings(towers.getString("$key.server", "")!!, towers.getString("$key.device", "")!!,
            towers.getString("$key.name", "")!!, towers.getInt("$key.age", 0),
            ConnectionEnvironment.entries.find { it.name == towers.getString("$key.environment", "DEVELOPMENT") } ?: ConnectionEnvironment.DEVELOPMENT)
    }.filter { it.environment == current().environment }.sortedBy { it.name }
}
