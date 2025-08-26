package de.materna.devsummit.components

import kotlinx.html.*
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter

internal fun MAIN.createSlideFooter() {
  div (classes = "mt-5 mb-2 text-center border-top") {
    id = "footer"
    div("row mt-2 justify-content-evenly") {
      col { +"© Materna 2025" }
      col { +"Shift Left on Steroids" }
      col { +"Max Sparrenberg & Constantin Ponfick" }
      col { +"${OffsetDateTime.now().format(DateTimeFormatter.ofPattern("dd.MM.yyyy"))}" }
    }
  }
}

private fun DIV.col(content: HtmlBlockTag.() -> Unit) {
  div("col-auto") { content() }
}