package com.hydromate.mobile.ui

import com.hydromate.mobile.R

/** Local, untinted artwork. Symbols are decorative and never encode a physical state. */
enum class GlassSymbol(val resource: Int, val navigationResource: Int = resource) {
    HOME(R.drawable.aero_home, R.drawable.nav_home),
    HISTORY(R.drawable.aero_history, R.drawable.nav_history),
    CULTIVATION(R.drawable.hero_hydromate_glass),
    CONTROL(R.drawable.aero_control, R.drawable.nav_control),
    SETTINGS(R.drawable.aero_settings, R.drawable.nav_settings),
    THERMOMETER(R.drawable.aero_thermometer),
    DROPLET(R.drawable.aero_droplet),
    CHEMISTRY(R.drawable.aero_chemistry),
    TDS(R.drawable.aero_tds),
    SUN(R.drawable.aero_sun),
    IRRIGATION(R.drawable.aero_irrigation)
}
