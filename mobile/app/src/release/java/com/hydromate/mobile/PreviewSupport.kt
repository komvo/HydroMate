package com.hydromate.mobile

import com.hydromate.mobile.ui.ReadingState

/** Release contains neither fixtures nor demo choices. */
object PreviewSupport {
    val options: List<String> = emptyList()
    fun referenceAge(@Suppress("UNUSED_PARAMETER") index: Int, configured: Int) = configured
    fun load(@Suppress("UNUSED_PARAMETER") index: Int): ReadingState? = null
}
