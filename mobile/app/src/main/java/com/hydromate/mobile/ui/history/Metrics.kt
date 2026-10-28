package com.hydromate.mobile.ui.history

import com.hydromate.mobile.Measurement
import java.time.Duration
import java.time.Instant
import java.util.Locale
import kotlin.math.abs
import kotlin.math.ceil
import kotlin.math.floor
import kotlin.math.log10
import kotlin.math.max
import kotlin.math.pow

/** Display metadata only; no metric carries a crop range or a good/bad judgement. */
enum class Metric(val title: String, val unit: String, val decimals: Int, val about: String,
                  val read: (Measurement) -> Double?) {
    PH("pH", "", 2, "Acidez o alcalinidad de la solución nutritiva, en escala de 0 a 14. Influye en qué nutrientes puede absorber la planta.", { it.ph }),
    TEMPERATURE("Temp.", "°C", 1, "Temperatura de la solución nutritiva medida por la sonda sumergida.", { it.temperature }),
    TDS("TDS", "ppm", 0, "Sólidos disueltos totales: estima la concentración de nutrientes a partir de la conductividad. Se compensa con la temperatura cuando está disponible.", { it.tds }),
    LIGHT("Luz", "% relativo", 0, "Iluminación que recibe la torre: lux en lecturas v2 o superiores, porcentaje relativo en registros v1.", { it.lightValue }),
    EC("EC", "µS/cm", 0, "Conductividad eléctrica de la solución nutritiva.", { it.ecUsCm });

    fun format(value: Double) = String.format(Locale.getDefault(), "%.${decimals}f", value)
    fun unitFor(rows: List<Measurement>) = if (this == LIGHT) rows.firstOrNull()?.lightUnit ?: unit else unit
}

data class Sample(val at: Instant, val value: Double)

/** Pure helpers for the trend chart; unit-tested on the JVM. */
object TrendMath {
    /** Oldest first; only rows with a value and, for light, the same unit as the newest row. */
    fun samples(rows: List<Measurement>, metric: Metric): List<Sample> {
        val unit = metric.unitFor(rows)
        return rows.filter { metric != Metric.LIGHT || it.lightUnit == unit }
            .mapNotNull { row -> metric.read(row)?.let { Sample(row.received, it) } }
            .sortedBy { it.at }
    }

    /**
     * Splits where an interval exceeds 3× the median interval, so the line never
     * draws continuity across missing receptions.
     */
    fun segments(samples: List<Sample>): List<List<Sample>> {
        if (samples.size < 3) return if (samples.isEmpty()) emptyList() else listOf(samples)
        val gaps = samples.zipWithNext { a, b -> Duration.between(a.at, b.at).toMillis() }
        val median = gaps.sorted()[gaps.size / 2].coerceAtLeast(1)
        val result = mutableListOf(mutableListOf(samples.first()))
        gaps.forEachIndexed { index, gap ->
            if (gap > median * 3) result.add(mutableListOf())
            result.last().add(samples[index + 1])
        }
        return result
    }

    /** Dynamic axis: rounded ticks that enclose every value, with padding for a flat series. */
    fun ticks(values: List<Double>): List<Double> {
        var low = values.min(); var high = values.max()
        if (high - low < 1e-9) { val pad = max(abs(high) * .02, .05); low -= pad; high += pad }
        val raw = (high - low) / 2
        val magnitude = 10.0.pow(floor(log10(raw)))
        val step = listOf(1.0, 2.0, 2.5, 5.0, 10.0).map { it * magnitude }.first { it >= raw - 1e-12 }
        val start = floor(low / step) * step
        val end = ceil(high / step) * step
        return generateSequence(start) { it + step }.takeWhile { it <= end + step * 1e-6 }.toList()
    }

    /** Plain-language change between the first and the last sample; null with fewer than two. */
    fun change(samples: List<Sample>, metric: Metric, unit: String): String? {
        if (samples.size < 2) return null
        val delta = samples.last().value - samples.first().value
        val span = duration(Duration.between(samples.first().at, samples.last().at))
        val shown = metric.format(abs(delta))
        val suffix = if (unit.isEmpty()) "" else " $unit"
        return when {
            metric.format(0.0) == shown -> "Sin cambio en $span"
            delta > 0 -> "Subió $shown$suffix en $span"
            else -> "Bajó $shown$suffix en $span"
        }
    }

    /** Arrow plus text so direction never relies on colour; neutral because no range exists. */
    fun step(previous: Double?, current: Double?, metric: Metric, unit: String = metric.unit): String? {
        if (previous == null || current == null) return null
        val delta = current - previous
        val shown = metric.format(abs(delta)) + if (unit.isEmpty() || unit.contains(' ')) "" else " $unit"
        return when {
            metric.format(abs(delta)) == metric.format(0.0) -> "= sin cambio"
            delta > 0 -> "↑ $shown vs. anterior"
            else -> "↓ $shown vs. anterior"
        }
    }

    fun duration(value: Duration): String {
        val minutes = value.toMinutes()
        return when {
            minutes < 1 -> "${value.seconds} s"
            minutes < 60 -> "$minutes min"
            minutes < 1440 -> "${minutes / 60} h${if (minutes % 60 > 0) " ${minutes % 60} min" else ""}"
            else -> "${minutes / 1440} d${if (minutes % 1440 >= 60) " ${minutes % 1440 / 60} h" else ""}"
        }
    }
}
