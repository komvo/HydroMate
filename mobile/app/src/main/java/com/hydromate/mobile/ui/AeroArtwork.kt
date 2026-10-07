package com.hydromate.mobile.ui

import android.graphics.*
import android.graphics.drawable.Drawable
import com.hydromate.mobile.R

/** Native translucent glass with a separate reading plate for text contrast. */
class AeroSurface(private val ui: Components, private val fill: Int,
                  private val glossy: Boolean = false, private val radius: Int = 20) : Drawable() {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    override fun isStateful() = true
    override fun getOutline(outline: Outline) {
        outline.setRoundRect(bounds, ui.dp(radius).toFloat()); outline.alpha = .32f
    }
    override fun onStateChange(state: IntArray): Boolean { invalidateSelf(); return true }
    override fun draw(canvas: Canvas) {
        val pressed=state.contains(android.R.attr.state_pressed)
        val focused=state.contains(android.R.attr.state_focused)
        val disabled=glossy && !state.contains(android.R.attr.state_enabled)
        val b=RectF(bounds).apply { inset(ui.dp(1).toFloat(),ui.dp(1).toFloat()) }
        val r=ui.dp(radius).toFloat()
        val base=if(disabled) ui.color(R.color.disabled_surface) else fill
        val light=ui.color(R.color.surface)
        val bottom=blend(base,ui.color(R.color.sky_deep),if(ui.night) .18f else .12f)
        paint.style=Paint.Style.FILL
        paint.alpha=if(ui.night) 180 else 110
        paint.shader=LinearGradient(0f,b.top,0f,b.bottom,
            intArrayOf(blend(base,light,.82f),blend(base,light,.48f),base,bottom,blend(base,light,.34f)),
            floatArrayOf(0f,.43f,.46f,.88f,1f),Shader.TileMode.CLAMP)
        canvas.drawRoundRect(b,r,r,paint); paint.shader=null
        if(!glossy) {
            val plate=RectF(b).apply { inset(ui.dp(4).toFloat(),ui.dp(5).toFloat()) }
            paint.color=blend(base,light,if(ui.night) .45f else .91f)
            paint.alpha=if(ui.night) 130 else 68
            canvas.drawRoundRect(plate,maxOf(0f,r-ui.dp(4)),maxOf(0f,r-ui.dp(4)),paint)
            paint.color=if(ui.night) 0x18FFFFFF else 0xADFFFFFF.toInt()
            canvas.drawRoundRect(b.left+r,b.top+ui.dp(2),b.right-r,b.top+ui.dp(6),r,r,paint)
        } else {
            val clip=Path().apply { addRoundRect(b,r,r,Path.Direction.CW) }
            canvas.save(); canvas.clipPath(clip)
            val reflection=Path().apply {
                moveTo(b.left,b.top); lineTo(b.right,b.top); lineTo(b.right,b.top+b.height()*.3f)
                cubicTo(b.right-b.width()*.2f,b.top+b.height()*.51f,
                    b.left+b.width()*.25f,b.top+b.height()*.49f,b.left,b.top+b.height()*.37f)
                close()
            }
            paint.color=if(ui.night) 0x18FFFFFF else if(pressed) 0x32FFFFFF else 0xADFFFFFF.toInt()
            canvas.drawPath(reflection,paint)
            canvas.restore()
        }
        if(pressed) {
            paint.color=if(ui.night) 0x1849C9F5 else 0x180B6EA9
            canvas.drawRoundRect(b,r,r,paint)
        }
        paint.style=Paint.Style.STROKE; paint.strokeWidth=ui.dp(if(focused) 3 else 1).toFloat()
        paint.color=if(focused) ui.ink else ui.color(R.color.outline)
        if(!focused) paint.shader=LinearGradient(b.left,b.top,b.right,b.bottom,
            intArrayOf(ui.color(R.color.outline),if(ui.night) 0xFF527E54.toInt() else 0xFFD4EDC2.toInt(),
                ui.color(R.color.outline)),floatArrayOf(0f,.42f,1f),Shader.TileMode.CLAMP)
        canvas.drawRoundRect(b,r,r,paint)
        paint.shader=null
        val inner=RectF(b).apply { inset(ui.dp(2).toFloat(),ui.dp(2).toFloat()) }
        paint.color=if(ui.night) 0x58E7FFCF else 0xEEFFFFFF.toInt()
        paint.strokeWidth=ui.dp(1).toFloat()
        canvas.drawRoundRect(inner,maxOf(0f,r-ui.dp(2)),maxOf(0f,r-ui.dp(2)),paint)
        // Fine edge reflections suggest thickness without crossing the reading plate.
        paint.strokeCap=Paint.Cap.ROUND
        paint.strokeWidth=ui.dp(1).toFloat()
        paint.shader=LinearGradient(b.left,b.top,b.right,b.top,
            intArrayOf(Color.TRANSPARENT,if(ui.night) 0x72E7FFCF else Color.WHITE,Color.TRANSPARENT),
            floatArrayOf(0f,.3f,1f),Shader.TileMode.CLAMP)
        canvas.drawLine(b.left+r,b.top+ui.dp(3),b.right-r,b.top+ui.dp(3),paint)
        paint.shader=LinearGradient(b.left,b.bottom,b.right,b.bottom,
            intArrayOf(Color.TRANSPARENT,if(ui.night) 0x5065B24A else 0xCCACDC78.toInt(),Color.TRANSPARENT),
            floatArrayOf(0f,.7f,1f),Shader.TileMode.CLAMP)
        canvas.drawLine(b.left+r,b.bottom-ui.dp(3),b.right-r,b.bottom-ui.dp(3),paint)
        paint.shader=null; paint.strokeCap=Paint.Cap.BUTT
    }
    override fun setAlpha(alpha: Int) = Unit
    override fun setColorFilter(colorFilter: ColorFilter?) { paint.colorFilter=colorFilter }
    @Deprecated("Drawable compatibility") override fun getOpacity() = PixelFormat.TRANSLUCENT
    private fun blend(a: Int,b: Int,t: Float)=Color.rgb(
        (Color.red(a)*(1-t)+Color.red(b)*t).toInt(),
        (Color.green(a)*(1-t)+Color.green(b)*t).toInt(),
        (Color.blue(a)*(1-t)+Color.blue(b)*t).toInt())
}

/** Static botanical backdrop. Image decoded once per screen container, never per frame. */
class AeroSky(private val ui: Components) : Drawable() {
    private val paint=Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG)
    private val foliage=BitmapFactory.decodeResource(ui.context.resources, R.drawable.background_botanical)
    private val destination=RectF()
    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)
        val scale=maxOf(bounds.width().toFloat()/foliage.width, bounds.height().toFloat()/foliage.height)
        val w=foliage.width*scale; val h=foliage.height*scale
        val x=bounds.exactCenterX()-w/2; val y=bounds.exactCenterY()-h/2
        destination.set(x,y,x+w,y+h)
    }
    override fun draw(canvas: Canvas) {
        paint.alpha=255; paint.shader=null; paint.style=Paint.Style.FILL
        canvas.save(); canvas.clipRect(bounds)
        canvas.drawBitmap(foliage,null,destination,paint)
        // A light mint veil creates the daytime garden; the system-night variant stays subdued.
        paint.color=if(ui.night) 0xBF05190F.toInt() else 0xBDEFFADD.toInt()
        canvas.drawRect(bounds,paint)
        canvas.restore()
    }
    override fun setAlpha(alpha: Int)=Unit
    override fun setColorFilter(colorFilter: ColorFilter?)=Unit
    @Deprecated("Drawable compatibility") override fun getOpacity()=PixelFormat.OPAQUE
}
