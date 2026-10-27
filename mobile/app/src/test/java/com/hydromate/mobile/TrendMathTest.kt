package com.hydromate.mobile

import com.hydromate.mobile.ui.history.Metric
import com.hydromate.mobile.ui.history.Sample
import com.hydromate.mobile.ui.history.TrendMath
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.time.Duration
import java.time.Instant

class TrendMathTest {
    private val start = Instant.parse("2026-10-21T02:00:00Z")
    // Display formatting follows the phone locale; pin it so expectations are stable.
    @Before fun locale() = java.util.Locale.setDefault(java.util.Locale.US)
    private fun at(minutes: Long, value: Double) = Sample(start.plusSeconds(minutes * 60), value)

    @Test fun gapLargerThanThreeMediansBreaksTheLine() {
        val samples = listOf(at(0, 1.0), at(1, 1.0), at(2, 1.0), at(3, 1.0), at(30, 2.0), at(31, 2.0))
        val segments = TrendMath.segments(samples)
        assertEquals(listOf(4, 2), segments.map { it.size })
        assertEquals(samples, segments.flatten())
    }

    @Test fun regularSeriesStaysOneSegment() {
        assertEquals(1, TrendMath.segments((0L..19L).map { at(it * 4, it.toDouble()) }).size)
        assertTrue(TrendMath.segments(emptyList()).isEmpty())
    }

    @Test fun ticksEncloseValuesAndHandleFlatSeries() {
        val ticks = TrendMath.ticks(listOf(6.1, 6.14, 6.18))
        assertTrue(ticks.first() <= 6.1 && ticks.last() >= 6.18 && ticks.size in 2..4)
        val flat = TrendMath.ticks(listOf(510.0, 510.0))
        assertTrue(flat.first() < 510.0 && flat.last() > 510.0)
    }

    @Test fun changeIsFactualAndUsesMetricPrecision() {
        assertEquals("Subió 0.08 en 1 h 16 min", TrendMath.change(listOf(at(0, 6.10), at(76, 6.18)), Metric.PH, ""))
        assertEquals("Bajó 38 ppm en 12 min", TrendMath.change(listOf(at(0, 548.0), at(12, 510.0)), Metric.TDS, "ppm"))
        assertEquals("Sin cambio en 4 min", TrendMath.change(listOf(at(0, 23.02), at(4, 23.04)), Metric.TEMPERATURE, "°C"))
        assertNull(TrendMath.change(listOf(at(0, 1.0)), Metric.PH, ""))
    }

    @Test fun stepNeedsBothValuesAndNeverJudges() {
        assertEquals("↑ 0.2 °C vs. anterior", TrendMath.step(23.0, 23.2, Metric.TEMPERATURE))
        assertEquals("↓ 0.04 vs. anterior", TrendMath.step(6.14, 6.10, Metric.PH))
        assertEquals("= sin cambio", TrendMath.step(510.0, 510.2, Metric.TDS))
        assertNull(TrendMath.step(null, 6.1, Metric.PH))
    }

    @Test fun samplesSkipMissingValuesInsteadOfUsingZero() {
        val rows = listOf(
            Measurement(2, "t", start.plusSeconds(60), 23.0, null, 510.0, 60.0, "MEDIA", 65.0, "MEDIO", true),
            Measurement(1, "t", start, 23.0, 6.1, 510.0, 60.0, "MEDIA", 65.0, "MEDIO", true))
        assertEquals(listOf(Sample(start, 6.1)), TrendMath.samples(rows, Metric.PH))
        assertEquals("2 d 3 h", TrendMath.duration(Duration.ofMinutes(2 * 1440 + 185)))
    }
}
