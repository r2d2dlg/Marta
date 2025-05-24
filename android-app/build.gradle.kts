// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.10.0")  // Downgraded to stable AGP
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.10")
        classpath("com.google.dagger:hilt-android-gradle-plugin:2.50") // Keep Hilt for now, will update next if needed
    }
}

plugins {
    id("com.android.application") version "8.10.0" apply false // Downgraded to stable AGP
    id("org.jetbrains.kotlin.android") version "1.9.10" apply false
    id("com.google.dagger.hilt.android") version "2.50" apply false
}

// Configure all projects to use Java 17
allprojects {
    tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
        kotlinOptions {
            jvmTarget = "17"
            freeCompilerArgs = freeCompilerArgs + listOf(
                "-Xjvm-default=all",  // Better Java interop
                "-opt-in=kotlin.RequiresOptIn"
            )
        }
    }
    
    tasks.withType<JavaCompile>().configureEach {
        sourceCompatibility = JavaVersion.VERSION_17.toString()
        targetCompatibility = JavaVersion.VERSION_17.toString()
        options.encoding = "UTF-8"
        options.isIncremental = true
    }
    
    // Configure Gradle wrapper to use the specified JDK
    tasks.withType<Wrapper> {
        gradleVersion = "8.4"
        distributionType = Wrapper.DistributionType.ALL
    }
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}

// Configure Java toolchains for all projects
subprojects {
    plugins.withType<JavaPlugin> {
        configure<JavaPluginExtension> {
            toolchain {
                languageVersion.set(org.gradle.jvm.toolchain.JavaLanguageVersion.of(17))
            }
        }
    }
    
    // Ensure Android projects use Java 17
    plugins.withId("com.android.application") {
        configure<com.android.build.gradle.BaseExtension> {
            compileOptions {
                sourceCompatibility = JavaVersion.VERSION_17
                targetCompatibility = JavaVersion.VERSION_17
            }
        }
    }
    
    plugins.withId("com.android.library") {
        configure<com.android.build.gradle.LibraryExtension> {
            compileOptions {
                sourceCompatibility = JavaVersion.VERSION_17
                targetCompatibility = JavaVersion.VERSION_17
            }
        }
    }
}
