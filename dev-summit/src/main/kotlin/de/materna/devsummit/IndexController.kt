package de.materna.devsummit

import de.materna.devsummit.components.index
import jakarta.servlet.http.HttpServletRequest
import kotlinx.html.div
import kotlinx.html.dom.createHTMLDocument
import kotlinx.html.dom.serialize
import kotlinx.html.unsafe
import org.springframework.core.io.Resource
import org.springframework.core.io.ResourceLoader
import org.springframework.core.io.support.ResourcePatternUtils
import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.servlet.resource.ResourceUrlProvider
import java.io.IOException

@Controller("")
class IndexController(
  private val resourceUrlProvider: ResourceUrlProvider,
  private val resourceLoader: ResourceLoader,
  private val markdownRenderer: MarkdownRenderer,
) {

  @GetMapping
  @ResponseBody
  fun getIndex(): String = index(resourceUrlProvider).serialize(true)

  @GetMapping("/{slideNumber}", produces = ["text/html"])
  @ResponseBody
  fun getIndexOnSlide(@PathVariable slideNumber: Long, request: HttpServletRequest): String {
    if (request.getHeader("hx-request") == "true")
      return getSlide(slideNumber)
    return index(resourceUrlProvider, slideNumber).serialize(true)
  }

  fun getSlide(@PathVariable slideNumber: Long): String {
    val content = try {
      val resource = loadResources(slidePattern(slideNumber)).firstOrNull()
      if (resource != null)
        markdownRenderer.renderMarkdownAsHtml(resource)
      else
        "Slide $slideNumber not found"
    } catch (e: Exception) {
      "Error rendering slide $slideNumber: ${e.message}"
    }

    return createHTMLDocument().div(
      "container-xxl pt-5"
    ) {
      unsafe { raw(content) }
    }.serialize(true)
  }

  @Throws(IOException::class)
  private fun loadResources(pattern: String): Array<Resource> {
    return ResourcePatternUtils.getResourcePatternResolver(resourceLoader).getResources(pattern)
  }

  private companion object {
    fun slidePattern(slideNumber: Long) = "classpath:/static/markdown/$slideNumber*.md"
  }

}