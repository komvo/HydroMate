import java.net.URI

plugins { id("com.android.application") }
android {
    buildFeatures { buildConfig = true }
    namespace = "com.hydromate.mobile"
    compileSdk { version = release(37) }
    defaultConfig {
        applicationId = "com.hydromate.mobile"
        minSdk = 26
        targetSdk = 35
        versionCode = 7
        versionName = "0.7.0-integration"
        // Read only the public URL from the versioned template, never a private .env.
        val defaultProductionUrl = providers.fileContents(rootProject.layout.projectDirectory.file("../.env.example"))
            .asText.map { text -> text.lineSequence().first { it.startsWith("HYDROMATE_APP_URL=") }.substringAfter('=') }
        val productionUrl = providers.environmentVariable("HYDROMATE_APP_URL").orElse(defaultProductionUrl).get().trim().trimEnd('/')
        if (productionUrl.isNotEmpty()) {
            val uri = URI(productionUrl)
            require(uri.scheme == "https" && !uri.host.isNullOrBlank() && uri.rawUserInfo == null
                && uri.rawQuery == null && uri.rawFragment == null && uri.path.isNullOrEmpty()
                && (uri.port == -1 || uri.port in 1..65535)) { "HYDROMATE_APP_URL must be an HTTPS base URL without /api or credentials" }
        }
        buildConfigField("String", "PRODUCTION_API_URL", "\"${productionUrl.replace("\\", "\\\\").replace("\"", "\\\"")}\"")
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
tasks.withType<org.gradle.api.tasks.testing.Test>().configureEach {
    // Test JVM only; never packaged in APK or used to relax Android TLS.
    providers.environmentVariable("HYDROMATE_TEST_TLS_TRUSTSTORE").orNull?.let {
        systemProperty("javax.net.ssl.trustStore", it)
        systemProperty("javax.net.ssl.trustStorePassword", "validation-only")
    }
}
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
}
