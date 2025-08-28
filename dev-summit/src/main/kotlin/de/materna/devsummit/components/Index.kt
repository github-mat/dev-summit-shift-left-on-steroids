package de.materna.devsummit.components

import de.materna.devsummit.hxGet
import de.materna.devsummit.hxPushUrl
import de.materna.devsummit.hxTarget
import de.materna.devsummit.hxTrigger
import kotlinx.html.*
import kotlinx.html.dom.createHTMLDocument
import org.springframework.web.servlet.resource.ResourceUrlProvider
import org.w3c.dom.Document

fun index(resourceUrlProvider: ResourceUrlProvider, slideNumber: Long = 0): Document = createHTMLDocument().html {
  createHead(resourceUrlProvider)
  createBody(slideNumber)
}

private fun HTML.createHead(resourceUrlProvider: ResourceUrlProvider) {
  head {
    metaTags()
    htmx()
    bootstrap()
    jQuery()
    highlightJs()
    internalDependencies(resourceUrlProvider)
    title { +"Shift Left on Steroids" }
  }
}

private fun HEAD.metaTags() {
  meta { charset = "UTF-8" }
  meta {
    content = "width=device-width, initial-scale=1.0"
    name = "viewport"
  }
  meta {
    content = "text/html; charset=utf-8"
    "http-equiv" to "Content-Type"
  }
}

private fun HEAD.htmx() {
  script(src = "https://unpkg.com/htmx.org@2.0.2", crossorigin = ScriptCrossorigin.anonymous) {
    integrity = "sha384-Y7hw+L/jvKeWIRRkqWYfPcvVxHzVzn5REgzbawhxAuQGwX1XWe70vji+VSeHOThJ"
  }
  meta {
    name = "htmx-config"
    content = "{\"allowNestedOobSwaps\": false, \"scrollBehavior\": \"smooth\"}"
  }
}

private fun HEAD.bootstrap() {
  link("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", "stylesheet") {
    attributes["crossorigin"] = "anonymous"
    integrity = "sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
  }
  script(
    ScriptType.textJavaScript,
    src = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
    crossorigin = ScriptCrossorigin.anonymous,
  ) {
    integrity = "sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
  }
  link(
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11/font/bootstrap-icons.min.css",
    "stylesheet",
  )
  script(
    ScriptType.textJavaScript,
    src = "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js",
  ) {}
}

private fun HEAD.jQuery() {
  script(
    type = ScriptType.textJavaScript,
    src = "https://code.jquery.com/jquery-3.7.1.slim.min.js",
    crossorigin = ScriptCrossorigin.anonymous,
  ) {
    integrity = "sha256-kmHvs0B+OpCW5GVHUNjv9rOmY0IvSIRcf7zGUDTDQM8="
  }
}

private fun HEAD.highlightJs() {
  link(
    "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/atom-one-dark.min.css",
    "stylesheet",
  )
  script(
    type = ScriptType.textJavaScript,
    src = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/highlight.js",
  ) {}
}

private fun HEAD.internalDependencies(resourceUrlProvider: ResourceUrlProvider) {
  link {
    rel = "icon"
    href = resourceUrlProvider.getForLookupPath("/images/favicon.ico")!!
  }
}

fun HTML.createBody(
  slideNumber: Long
) {
  classes = setOf("bg-dark")
  body {
    id = "body"
    classes = setOf("bg-black", "d-flex", "justify-content-center", "align-items-center", "m-0")
    main {
      createSlideHeader()
      id = "main"
      classes = setOf("bg-white", "rounded", "shadow", "d-flex", "flex-column", "justify-content-center", "align-items-stretch", "w-100")
      style = "min-width: 2000px; max-width: 80vh; min-height: 100vh; height: 70vh; display: flex; flex-direction: column;"
      div {
        id = "slide-content"
        style = "flex: 1 0 auto; width: 100%;"
        loadMainElement("/$slideNumber")
      }
      createSlideFooter()
    }

  }
}

private fun DIV.loadMainElement(page: String) {
  // Only set HTMX attributes on the slide-content div
  hxPushUrl()
  hxGet(page)
  hxTarget("#slide-content")
  hxTrigger("load")
}