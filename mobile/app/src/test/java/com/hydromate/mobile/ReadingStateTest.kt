package com.hydromate.mobile

import com.hydromate.mobile.ui.*
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException
import java.net.SocketTimeoutException
import java.time.Instant

class ReadingStateTest {
    private val now = Instant.parse("2026-10-03T20:00:00Z")

    @Test fun distinguishesNetworkTimeoutInvalidDataAndServerFailure() {
        assertEquals(FailureKind.NETWORK, failure(IOException("host unreachable")).kind)
        assertEquals(FailureKind.TIMEOUT, failure(SocketTimeoutException()).kind)
        assertEquals(FailureKind.INVALID, failure(org.json.JSONException("missing sensor")).kind)
        assertEquals(FailureKind.INVALID, failure(IllegalArgumentException("wrong tower")).kind)
        assertEquals(FailureKind.SERVER, failure(TelemetryHttpException(503)).kind)
        assertEquals(FailureKind.AUTH, failure(TelemetryHttpException(401)).kind)
        assertEquals(FailureKind.AUTH, failure(TelemetryHttpException(403)).kind)
        assertEquals(FailureKind.PARAMETERS, failure(TelemetryHttpException(422)).kind)
    }

    @Test fun freshnessIsOptInAndUsesReceptionTime() {
        val earlier = now.minusSeconds(3600)
        assertFalse(isOld(earlier, now, 0))
        assertFalse(isOld(now.minusSeconds(59), now, 1))
        assertTrue(isOld(now.minusSeconds(60), now, 1))
        assertTrue(isOld(earlier, now, 30))
        assertFalse(isOld(now.plusSeconds(60), now, 1))
    }

    @Test fun reportsFutureTimestampWithoutClaimingFreshness() {
        assertTrue(relativeTime(now.plusSeconds(60), now).contains("adelantada"))
        assertEquals("hace unos segundos", relativeTime(now.minusSeconds(10), now))
        assertEquals("hace 2 min", relativeTime(now.minusSeconds(120), now))
        assertEquals("hace 2 h", relativeTime(now.minusSeconds(7200), now))
        assertEquals("hace 2 días", relativeTime(now.minusSeconds(172800), now))
    }
}
