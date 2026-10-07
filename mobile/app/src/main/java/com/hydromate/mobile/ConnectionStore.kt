package com.hydromate.mobile

import android.content.Context
import com.hydromate.mobile.ui.settings.ConnectionSettings

/** Names/age preferences belong to a server + tower; no telemetry is persisted. */
class ConnectionStore(context: Context) {
    private val active = context.getSharedPreferences("connection", Context.MODE_PRIVATE)
    private val towers = context.getSharedPreferences("tower_settings", Context.MODE_PRIVATE)
    fun current() = ConnectionSettings(active.getString("server", "http://127.0.0.1:8000")!!,
        active.getString("device", "test-api-0865fd385681")!!,
        active.getString("name", "Torre principal")!!, active.getInt("age_minutes", 0))
    fun save(config: ConnectionSettings) {
        active.edit().putString("server", config.server).putString("device", config.device)
            .putString("name", config.name).putInt("age_minutes", config.ageMinutes).apply()
        val key = java.security.MessageDigest.getInstance("SHA-256")
            .digest("${config.server}\n${config.device}".toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
        val keys = towers.getStringSet("keys", emptySet())!!.toMutableSet().apply { add(key) }
        towers.edit().putStringSet("keys", keys).putString("$key.server", config.server)
            .putString("$key.device", config.device).putString("$key.name", config.name)
            .putInt("$key.age", config.ageMinutes).apply()
    }
    fun saved(): List<ConnectionSettings> = towers.getStringSet("keys", emptySet())!!.map { key ->
        ConnectionSettings(towers.getString("$key.server", "")!!, towers.getString("$key.device", "")!!,
            towers.getString("$key.name", "")!!, towers.getInt("$key.age", 0))
    }.sortedBy { it.name }
}
