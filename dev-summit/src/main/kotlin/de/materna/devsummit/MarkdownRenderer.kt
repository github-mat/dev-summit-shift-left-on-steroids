package de.materna.devsummit

import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.util.stream.Collectors
import org.commonmark.ext.gfm.tables.*
import org.commonmark.ext.image.attributes.ImageAttributesExtension
import org.commonmark.ext.task.list.items.TaskListItemsExtension
import org.commonmark.node.BlockQuote
import org.commonmark.node.Node
import org.commonmark.node.Text
import org.commonmark.parser.Parser
import org.commonmark.renderer.NodeRenderer
import org.commonmark.renderer.html.AttributeProvider
import org.commonmark.renderer.html.HtmlNodeRendererContext
import org.commonmark.renderer.html.HtmlRenderer
import org.commonmark.renderer.html.HtmlWriter
import org.springframework.core.io.Resource
import org.springframework.stereotype.Component

@Component
class MarkdownRenderer {

  @Throws(IOException::class)
  fun renderMarkdownAsHtml(resource: Resource): String {
    val reader = BufferedReader(InputStreamReader(resource.inputStream))
    val md = reader.lines().collect(Collectors.joining(System.lineSeparator()))
    return renderMarkdownAsHtml(md)
  }

  fun renderMarkdownAsHtml(markdown: String?): String {
    val sb = StringBuilder()
    val document = parser.parse(markdown)
    render.render(document, sb)
    return sb.toString()
  }

  companion object {
    private val extensions =
      listOf(
        TablesExtension.create(),
        TaskListItemsExtension.create(),
        ImageAttributesExtension.create(),
      )
    val parser: Parser = Parser.builder().extensions(extensions).build()
    val render: HtmlRenderer =
      HtmlRenderer.builder()
        .extensions(extensions)
        .nodeRendererFactory { context: HtmlNodeRendererContext -> BlockQuoteRenderer(context) }
        .attributeProviderFactory { TableAttributeProvider() }
        .build()
  }
}

private class BlockQuoteRenderer(context: HtmlNodeRendererContext) : NodeRenderer {
  private val html: HtmlWriter = context.writer

  override fun getNodeTypes(): Set<Class<out Node>> {
    // Return the node types we want to use this renderer for.
    return mutableSetOf<Class<out Node>>(BlockQuote::class.java)
  }

  override fun render(node: Node) {
    val split = getQuoteContent(node as BlockQuote)
    html.line()
    html.tag("figure", mapOf(("class" to "text-end mb-5 mt-5")))
    html.line()
    html.tag("blockquote", mapOf(("class" to "blockquote")))
    html.text(split[0])
    html.tag("/blockquote")
    html.line()
    if (split.size == 2) {
      html.tag("figcaption", mapOf(("class" to "blockquote-footer")))
      html.text(split[1])
      html.tag("/figcaption")
      html.line()
    }
    html.tag("/figure")
    html.line()
  }

  companion object {
    private fun getQuoteContent(node: BlockQuote): Array<String> {
      val content = collectContent(node)
      val split = content.split("~".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
      require(split.size <= 2) {
        "Blockquote content must be in the format: \"quote~author\" or \"quote\""
      }

      return split
    }

    private fun collectContent(node: BlockQuote): String {
      val content = StringBuilder()
      var child = node.firstChild.firstChild
      while (child != null) {
        if (child is Text) {
          if (content.isNotEmpty() && child.getNext() != null) {
            content.append(" ")
          }
          content.append(child.literal)
        }
        child = child.next
      }
      return content.toString()
    }
  }
}

private class TableAttributeProvider : AttributeProvider {
  override fun setAttributes(node: Node, tagName: String, attributes: MutableMap<String, String>) {
    if (node is TableBlock) {
      attributes["class"] = "table table-responsive align-middle"
    }
    if (node is TableBody) {
      attributes["class"] = "table-group-divider"
    }
    if (node.parent.parent is TableHead && node is TableCell && tagName == "th") {
      attributes["scope"] = "col"
      if (attributes["align"] == "center") {
        attributes["class"] = "text-center"
      } else if (attributes["align"] == "right") {
        attributes["class"] = "text-end"
      } else {
        attributes["class"] = "text-start"
      }
    }
  }
}