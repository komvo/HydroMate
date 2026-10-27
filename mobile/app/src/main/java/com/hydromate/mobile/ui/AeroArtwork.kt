package com.hydromate.mobile.ui

import android.graphics.*
import android.graphics.drawable.Drawable
import android.view.View
import android.view.ViewTreeObserver
import com.hydromate.mobile.R
import java.util.Collections
import java.util.WeakHashMap

/**
 * Glass roles inspired by Apple's Liquid Glass hierarchy:
 * PANEL/TINTED/FIELD belong to the content layer; CONTROL, PROMINENT and SELECTED
 * form the floating controls layer (navigation, buttons, segmented selection).
 */
enum class GlassStyle { PANEL, TINTED, FIELD, CONTROL, PROMINENT, SELECTED }

/** Corner radius sentinel: half of the shortest side, giving a capsule. */
const val CAPSULE = -1

/**
 * One static botanical backdrop per screen container. The photo is decoded once and a
 * small blurred, saturated copy is prepared once; glass surfaces sample that copy at
 * their window position, so they frost the leaves behind them without per-frame blur.
 * Content that scrolls beneath glass is not refracted; only the local background is.
 */
class GlassBackdrop(private val ui: Components) {
    val photo: Bitmap = BitmapFactory.decodeResource(ui.context.resources, R.drawable.background_botanical)
    private val frosted: Bitmap = frost(photo)
    private val shader = BitmapShader(frosted, Shader.TileMode.CLAMP, Shader.TileMode.CLAMP)
    private val matrix = Matrix()
    private val hosts: MutableSet<View> = Collections.newSetFromMap(WeakHashMap())
    private val hostLocation = IntArray(2)
    private val originLocation = IntArray(2)
    private var origin: View? = null
    private val refresh = ViewTreeObserver.OnScrollChangedListener { invalidateHosts() }
    private val relayout = ViewTreeObserver.OnGlobalLayoutListener { invalidateHosts() }

    /** The view whose full bounds show the sharp backdrop (AeroSky). */
    fun attach(view: View) {
        origin = view
        view.viewTreeObserver.addOnScrollChangedListener(refresh)
        view.viewTreeObserver.addOnGlobalLayoutListener(relayout)
    }

    /** Hardware display lists are reused while scrolling; glass must redraw at its new offset. */
    private fun invalidateHosts() = hosts.toList().forEach { it.invalidate() }

    /** Center-crop placement shared by the sharp backdrop and the frosted copy. */
    fun placement(width: Int, height: Int): RectF {
        val scale = maxOf(width.toFloat() / photo.width, height.toFloat() / photo.height)
        val w = photo.width * scale; val h = photo.height * scale
        return RectF((width - w) / 2, (height - h) / 2, (width + w) / 2, (height + h) / 2)
    }

    /** Paints the frosted backdrop under [host]; false when no position is available yet. */
    fun paint(canvas: Canvas, host: View?, bounds: Rect, paint: Paint): Boolean {
        val frame = origin ?: return false
        if (host == null || !host.isAttachedToWindow || frame.width == 0) return false
        hosts.add(host)
        host.getLocationInWindow(hostLocation); frame.getLocationInWindow(originLocation)
        val place = placement(frame.width, frame.height)
        matrix.setScale(place.width() / frosted.width, place.height() / frosted.height)
        matrix.postTranslate(place.left - (hostLocation[0] - originLocation[0]),
            place.top - (hostLocation[1] - originLocation[1]))
        shader.setLocalMatrix(matrix)
        paint.shader = shader; paint.alpha = 255
        canvas.drawRect(bounds, paint)
        paint.shader = null
        return true
    }

    private fun frost(source: Bitmap): Bitmap {
        val small = Bitmap.createScaledBitmap(source, maxOf(1, source.width / 8), maxOf(1, source.height / 8), true)
        val w = small.width; val h = small.height
        val pixels = IntArray(w * h).also { small.getPixels(it, 0, w, 0, 0, w, h) }
        repeat(3) { boxBlur(pixels, w, h, 3) }
        val out = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        out.setPixels(pixels, 0, w, 0, 0, w, h)
        // Liquid Glass keeps colour alive under the blur: lift saturation, then veil it for text.
        val canvas = Canvas(out)
        val saturate = Paint().apply { colorFilter = ColorMatrixColorFilter(ColorMatrix().apply { setSaturation(1.35f) }) }
        canvas.drawBitmap(out.copy(Bitmap.Config.ARGB_8888, false), 0f, 0f, saturate)
        canvas.drawColor(ui.withAlpha(ui.color(R.color.veil), if (ui.night) 0x99 else 0x80))
        return out
    }

    private fun boxBlur(pixels: IntArray, w: Int, h: Int, radius: Int) {
        val copy = IntArray(pixels.size)
        fun pass(read: IntArray, write: IntArray, horizontal: Boolean) {
            val lines = if (horizontal) h else w; val length = if (horizontal) w else h
            for (line in 0 until lines) for (i in 0 until length) {
                var r = 0; var g = 0; var b = 0; var n = 0
                for (k in -radius..radius) {
                    val j = (i + k).coerceIn(0, length - 1)
                    val p = read[if (horizontal) line * w + j else j * w + line]
                    r += Color.red(p); g += Color.green(p); b += Color.blue(p); n++
                }
                write[if (horizontal) line * w + i else i * w + line] = Color.rgb(r / n, g / n, b / n)
            }
        }
        pass(pixels, copy, true); pass(copy, pixels, false)
    }
}

/**
 * Native glass: frosted backdrop, tint, soft top sheen, specular rim and, for controls,
 * an inner lens band that suggests thickness. Reflections stay inside the outline.
 */
class GlassSurface(private val ui: Components, private val style: GlassStyle = GlassStyle.PANEL,
                   private val radius: Int = 26, private val tint: Int? = null) : Drawable() {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG)
    private val shape = Path()
    private val box = RectF()
    override fun isStateful() = true
    override fun onStateChange(state: IntArray): Boolean { invalidateSelf(); return true }
    private fun cornerRadius(rect: RectF) =
        // Capsules cap at 40 dp so multi-line text at large font sizes stays a rounded rectangle, not an oval.
        if (radius == CAPSULE) minOf(minOf(rect.width(), rect.height()) / 2, ui.dp(40).toFloat()) else minOf(ui.dp(radius).toFloat(), minOf(rect.width(), rect.height()) / 2)
    override fun getOutline(outline: Outline) {
        box.set(bounds)
        outline.setRoundRect(bounds, cornerRadius(box))
        outline.alpha = if (style == GlassStyle.CONTROL || style == GlassStyle.PROMINENT) .5f else .28f
    }
    override fun draw(canvas: Canvas) {
        val pressed = state.contains(android.R.attr.state_pressed)
        val focused = state.contains(android.R.attr.state_focused)
        val disabled = !state.contains(android.R.attr.state_enabled) &&
            (style == GlassStyle.CONTROL || style == GlassStyle.PROMINENT)
        val night = ui.night
        box.set(bounds); box.inset(ui.dp(1) / 2f, ui.dp(1) / 2f)
        val r = cornerRadius(box)
        shape.reset(); shape.addRoundRect(box, r, r, Path.Direction.CW)

        canvas.save(); canvas.clipPath(shape)
        paint.style = Paint.Style.FILL
        if (style != GlassStyle.SELECTED && !ui.backdrop.paint(canvas, host(), bounds, paint)) {
            paint.color = ui.color(R.color.background); canvas.drawRect(box, paint)
        }
        when (style) {
            GlassStyle.PROMINENT -> {
                paint.shader = LinearGradient(0f, box.top, 0f, box.bottom,
                    ui.withAlpha(ui.color(R.color.prominent_top), 0xF2), ui.withAlpha(ui.color(R.color.prominent_bottom), 0xF5), Shader.TileMode.CLAMP)
                canvas.drawRect(box, paint); paint.shader = null
            }
            else -> {
                val (base, alpha) = when (style) {
                    GlassStyle.PANEL -> ui.color(R.color.surface) to if (night) 0xB8 else 0xA8
                    GlassStyle.TINTED -> (tint ?: ui.color(R.color.glass)) to if (night) 0xC0 else 0xB8
                    GlassStyle.FIELD -> ui.color(R.color.glass_control) to if (night) 0xC8 else 0xD0
                    GlassStyle.CONTROL -> ui.color(R.color.glass_control) to if (night) 0xB0 else 0x9C
                    else -> ui.color(R.color.selected) to 0xE0
                }
                paint.color = ui.withAlpha(base, alpha); canvas.drawRect(box, paint)
            }
        }
        if (disabled) { paint.color = ui.withAlpha(ui.color(R.color.disabled_surface), 0xB0); canvas.drawRect(box, paint) }
        // Soft sheen: a gentle falloff, not the hard half-reflection of classic web buttons.
        val sheenDepth = if (style == GlassStyle.PANEL || style == GlassStyle.TINTED) .32f else .55f
        val sheen = if (night) 0x1EFFFFFF else if (style == GlassStyle.FIELD) 0x00FFFFFF else 0x55FFFFFF
        paint.shader = LinearGradient(0f, box.top, 0f, box.top + box.height() * sheenDepth,
            sheen, Color.TRANSPARENT, Shader.TileMode.CLAMP)
        canvas.drawRect(box, paint); paint.shader = null
        if (style == GlassStyle.FIELD) {
            // Recessed well: a faint inner shadow along the top edge.
            paint.shader = LinearGradient(0f, box.top, 0f, box.top + ui.dp(6), if (night) 0x40000000 else 0x1A10301F, Color.TRANSPARENT, Shader.TileMode.CLAMP)
            canvas.drawRect(box, paint); paint.shader = null
        }
        if (pressed) { paint.color = if (night) 0x26FFFFFF else 0x3DFFFFFF; canvas.drawRect(box, paint) }
        canvas.restore()

        paint.style = Paint.Style.STROKE
        if (style == GlassStyle.CONTROL || style == GlassStyle.PROMINENT || style == GlassStyle.SELECTED) {
            // Lens band: light gathers at the upper edge and darkens slightly below, suggesting thickness.
            val lens = RectF(box).apply { inset(ui.dp(2).toFloat(), ui.dp(2).toFloat()) }
            paint.strokeWidth = ui.dp(3).toFloat()
            paint.shader = LinearGradient(0f, lens.top, 0f, lens.bottom,
                intArrayOf(if (night) 0x40FFFFFF else 0x99FFFFFF.toInt(), Color.TRANSPARENT, if (night) 0x24000000 else 0x14103020),
                floatArrayOf(0f, .5f, 1f), Shader.TileMode.CLAMP)
            canvas.drawRoundRect(lens, maxOf(0f, r - ui.dp(2)), maxOf(0f, r - ui.dp(2)), paint)
        }
        // Specular rim: bright at the top-left, fading, catching again at the bottom-right.
        paint.strokeWidth = ui.dp(1).toFloat()
        val rimStrong = if (night) 0x8CE7FFCF.toInt() else 0xF2FFFFFF.toInt()
        val rimSoft = if (night) 0x26E7FFCF else 0x40FFFFFF
        paint.shader = LinearGradient(box.left, box.top, box.right, box.bottom,
            intArrayOf(rimStrong, rimSoft, if (night) 0x18FFFFFF else 0x30FFFFFF, rimStrong),
            floatArrayOf(0f, .35f, .7f, 1f), Shader.TileMode.CLAMP)
        canvas.drawRoundRect(box, r, r, paint); paint.shader = null
        if (style == GlassStyle.PANEL || style == GlassStyle.TINTED || style == GlassStyle.FIELD) {
            paint.color = ui.withAlpha(ui.color(R.color.sky_deep), if (night) 0x40 else 0x22)
            val outer = RectF(box).apply { inset(-ui.dp(1) / 2f, -ui.dp(1) / 2f) }
            canvas.drawRoundRect(outer, r + ui.dp(1) / 2f, r + ui.dp(1) / 2f, paint)
        }
        if (focused) {
            paint.strokeWidth = ui.dp(3).toFloat(); paint.color = ui.primary
            val ring = RectF(box).apply { inset(ui.dp(1).toFloat(), ui.dp(1).toFloat()) }
            canvas.drawRoundRect(ring, maxOf(0f, r - ui.dp(1)), maxOf(0f, r - ui.dp(1)), paint)
        }
        paint.style = Paint.Style.FILL
    }
    /** The owning view, also when wrapped by a StateListDrawable. */
    private fun host(): View? {
        var owner: Any? = callback
        while (owner is Drawable) owner = owner.callback
        return owner as? View
    }
    override fun setAlpha(alpha: Int) = Unit
    override fun setColorFilter(colorFilter: ColorFilter?) { paint.colorFilter = colorFilter }
    @Deprecated("Drawable compatibility") override fun getOpacity() = PixelFormat.TRANSLUCENT
}

/** Sharp botanical backdrop with a light veil; stronger at the top for large titles. */
class AeroSky(private val ui: Components) : Drawable() {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG)
    private var destination = RectF()
    private var veil: Shader? = null
    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)
        destination = ui.backdrop.placement(bounds.width(), bounds.height()).apply { offset(bounds.left.toFloat(), bounds.top.toFloat()) }
        val v = ui.color(R.color.veil)
        veil = LinearGradient(0f, bounds.top.toFloat(), 0f, bounds.bottom.toFloat(),
            intArrayOf(ui.withAlpha(v, if (ui.night) 0xCC else 0xC8), ui.withAlpha(v, if (ui.night) 0xBC else 0xAC),
                ui.withAlpha(v, if (ui.night) 0xC4 else 0xB8)),
            floatArrayOf(0f, .4f, 1f), Shader.TileMode.CLAMP)
    }
    override fun draw(canvas: Canvas) {
        canvas.save(); canvas.clipRect(bounds)
        paint.shader = null; paint.alpha = 255
        canvas.drawBitmap(ui.backdrop.photo, null, destination, paint)
        paint.shader = veil; canvas.drawRect(bounds, paint); paint.shader = null
        canvas.restore()
    }
    override fun setAlpha(alpha: Int) = Unit
    override fun setColorFilter(colorFilter: ColorFilter?) = Unit
    @Deprecated("Drawable compatibility") override fun getOpacity() = PixelFormat.OPAQUE
}

/** Small decorative leaf drawn natively; used beside section titles. Never encodes state. */
class LeafGlyph(private val ui: Components) : Drawable() {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val leaf = Path()
    override fun draw(canvas: Canvas) {
        val b = RectF(bounds)
        leaf.reset()
        leaf.moveTo(b.left + b.width() * .12f, b.bottom - b.height() * .1f)
        leaf.cubicTo(b.left, b.top + b.height() * .35f, b.left + b.width() * .45f, b.top, b.right - b.width() * .05f, b.top + b.height() * .05f)
        leaf.cubicTo(b.right, b.top + b.height() * .55f, b.left + b.width() * .6f, b.bottom, b.left + b.width() * .12f, b.bottom - b.height() * .1f)
        leaf.close()
        paint.style = Paint.Style.FILL
        paint.shader = LinearGradient(b.left, b.bottom, b.right, b.top,
            ui.color(R.color.leaf_deep), ui.color(R.color.leaf_light), Shader.TileMode.CLAMP)
        canvas.drawPath(leaf, paint); paint.shader = null
        paint.style = Paint.Style.STROKE; paint.strokeWidth = b.width() * .07f; paint.strokeCap = Paint.Cap.ROUND
        paint.color = if (ui.night) 0x99103020.toInt() else 0xCCFFFFFF.toInt()
        canvas.drawLine(b.left + b.width() * .14f, b.bottom - b.height() * .14f, b.right - b.width() * .22f, b.top + b.height() * .22f, paint)
    }
    override fun setAlpha(alpha: Int) = Unit
    override fun setColorFilter(colorFilter: ColorFilter?) { paint.colorFilter = colorFilter }
    @Deprecated("Drawable compatibility") override fun getOpacity() = PixelFormat.TRANSLUCENT
}
