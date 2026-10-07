plugins { id("com.android.application") }
android {
    namespace = "com.hydromate.mobile"
    compileSdk { version = release(37) }
    defaultConfig {
        applicationId = "com.hydromate.mobile"
        minSdk = 26
        targetSdk = 35
        versionCode = 6
        versionName = "0.6.0-garden"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
}
