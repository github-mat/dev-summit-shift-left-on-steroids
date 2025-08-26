package de.materna.devsummit


import kotlinx.html.HTMLTag

fun HTMLTag.hxGet(value: String) {
  attributes += "hx-get" to value
}

fun HTMLTag.hxPost(value: String) {
  attributes += "hx-post" to value
}

fun HTMLTag.hxPut(value: String) {
  attributes += "hx-put" to value
}

fun HTMLTag.hxTarget(value: String) {
  attributes += "hx-target" to value
}

fun HTMLTag.hxConfirm(value: String) {
  attributes += "hx-confirm" to value
}

fun HTMLTag.hxDelete(value: String) {
  attributes += "hx-delete" to value
}

fun HTMLTag.hxPushUrl(value: Boolean) {
  attributes += "hx-push-url" to value.toString()
}

fun HTMLTag.hxPushUrl() {
  attributes += "hx-push-url" to "true"
}

fun HTMLTag.hxSwap(value: String) {
  attributes += "hx-swap" to value
}

fun HTMLTag.hxSwapOob(value: String) {
  attributes += "hx-swap-oob" to value
}

fun HTMLTag.hxTrigger(value: String) {
  attributes += "hx-trigger" to value
}

fun HTMLTag.hxIndicator(value: String) {
  attributes += "hx-indicator" to value
}

fun HTMLTag.hxHistory(value: Boolean) {
  attributes += "hx-history" to value.toString()
}

fun HTMLTag.hxHistoryElt() {
  attributes += "hx-history-elt" to ""
}