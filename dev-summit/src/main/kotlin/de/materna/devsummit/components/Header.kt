package de.materna.devsummit.components

import kotlinx.html.*

internal fun MAIN.createSlideHeader() {
  div(classes = "bg-light sticky-top") {
    style = "height: 56px"
    id = "header"
    navbar()
  }
}


private fun DIV.navbar() {
  nav {
  }
}
