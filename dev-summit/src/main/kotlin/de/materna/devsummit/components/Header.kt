package de.materna.devsummit.components

import kotlinx.html.*

internal fun BODY.createHeader() {
  header(classes = "sticky-top") {
    id = "header"
    navbar()
  }
}


private fun HEADER.navbar() {
  nav {
    style = "background-color: #e0e0e0; height: 56px; width: 100%;"
  }
}
