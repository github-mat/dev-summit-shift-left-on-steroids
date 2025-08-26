plugins {
  kotlin("jvm") version "1.9.25"
  kotlin("plugin.spring") version "1.9.25"
  id("org.springframework.boot") version "3.5.5"
  id("io.spring.dependency-management") version "1.1.7"
}

group = "de.materna"
version = "0.0.1-SNAPSHOT"
description = "dev-summit"

java {
  toolchain {
    languageVersion = JavaLanguageVersion.of(21)
  }
}

repositories {
  mavenCentral()
}

val commonMarkVersion = "0.24.0"
val kotlinHtml = "0.12.0"

dependencies {
  implementation("org.springframework.boot:spring-boot-starter-web")
  implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
  implementation("org.jetbrains.kotlin:kotlin-reflect")
  implementation("org.commonmark:commonmark:$commonMarkVersion")
  implementation("org.commonmark:commonmark-ext-gfm-tables:$commonMarkVersion")
  implementation("org.commonmark:commonmark-ext-image-attributes:$commonMarkVersion")
  implementation("org.commonmark:commonmark-ext-task-list-items:$commonMarkVersion")
  implementation("org.jetbrains.kotlinx:kotlinx-html-jvm:$kotlinHtml")
  developmentOnly("org.springframework.boot:spring-boot-devtools")
  testImplementation("org.springframework.boot:spring-boot-starter-test")
  testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
  testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

kotlin {
  compilerOptions {
    freeCompilerArgs.addAll("-Xjsr305=strict")
  }
}

tasks.withType<Test> {
  useJUnitPlatform()
}
