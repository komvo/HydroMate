package com.hydromate.mobile

import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

class RepositoryTest {
    @Test fun reportsServerErrorsAndEmptyHistoryOverHttp() {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/empty") { exchange ->
            val body = "[]".toByteArray()
            exchange.sendResponseHeaders(200, body.size.toLong())
            exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/error") { exchange ->
            exchange.sendResponseHeaders(503, -1); exchange.close()
        }
        server.start()
        try {
            val base = "http://127.0.0.1:${server.address.port}"
            assertTrue(TelemetryRepository().load("$base/empty", "test").isEmpty())
            val error = assertThrows(IllegalStateException::class.java) { TelemetryRepository().load("$base/error", "test") }
            assertTrue(error.message!!.contains("503"))
        } finally { server.stop(0) }
    }

    @Test fun readsExistingSyntheticDeviceFromLocalLaravelWhenRequested() {
        val base = System.getenv("HYDROMATE_TEST_API")
        assumeTrue("Opt-in read-only integration test", !base.isNullOrBlank())
        val id = "test-api-0865fd385681"
        val rows = TelemetryRepository().load(Telemetry.endpoint(base!!, id), id)
        assertTrue(rows.isNotEmpty())
        assertTrue(rows.all { it.device == id && it.synthetic })
        val emptyId = "test-android-empty-846271"
        assertTrue(TelemetryRepository().load(Telemetry.endpoint(base, emptyId), emptyId).isEmpty())
    }
}
