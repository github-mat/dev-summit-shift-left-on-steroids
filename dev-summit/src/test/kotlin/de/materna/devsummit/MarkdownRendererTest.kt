package de.materna.devsummit

import org.assertj.core.api.Assertions
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.mockito.InjectMocks
import org.mockito.junit.jupiter.MockitoExtension

@ExtendWith(MockitoExtension::class)
class MarkdownRendererTest {
  @InjectMocks
  private val markdownRenderer: MarkdownRenderer? = null

  @Nested
  internal inner class RenderMarkdownAsHtml {
    @Test
    fun header() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml("# header")
      val expected = "<h1>header</h1>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun bold() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml("**bold**")
      val expected = "<p><strong>bold</strong></p>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun italic() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml("*italic*")
      val expected = "<p><em>italic</em></p>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun code() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml("`code`")
      val expected = "<p><code>code</code></p>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render link`() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml("[link](https://www.example.com)")
      val expected = "<p><a href=\"https://www.example.com\">link</a></p>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render image`() {
      val actual =
        markdownRenderer!!.renderMarkdownAsHtml("![image](https://www.example.com/image.jpg)")
      val expected = "<p><img src=\"https://www.example.com/image.jpg\" alt=\"image\" /></p>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render unordered list`() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml("- item1\n- item2")
      val expected = "<ul>\n<li>item1</li>\n<li>item2</li>\n</ul>\n"
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render block quote without caption`() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml(">I am a quote")
      val expected =
        """
          <figure class="text-end mb-5 mt-5">
          <blockquote class="blockquote">I am a quote</blockquote>
          </figure>
          
          """
          .trimIndent()
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render block quote with caption`() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml(">I am a quote~author")
      val expected =
        """
          <figure class="text-end mb-5 mt-5">
          <blockquote class="blockquote">I am a quote</blockquote>
          <figcaption class="blockquote-footer">author</figcaption>
          </figure>
          
          """
          .trimIndent()
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render block quote with linebreak`() {
      val actual = markdownRenderer!!.renderMarkdownAsHtml(">I am a quote\n> test\n> ~author")
      val expected =
        """
              <figure class="text-end mb-5 mt-5">
              <blockquote class="blockquote">I am a quote test</blockquote>
              <figcaption class="blockquote-footer">author</figcaption>
              </figure>
              
              """
          .trimIndent()
      Assertions.assertThat(actual).isEqualTo(expected)
    }

    @Test
    fun `render complex document`() {
      val actual =
        markdownRenderer!!.renderMarkdownAsHtml(
          """
              # header
              **bold**
              *italic*
              `code`
              [link](https://www.example.com)
              ![image](https://www.example.com/image.jpg)
              - item1
              - item2
              """
            .trimIndent()
        )
      val expected =
        """
          <h1>header</h1>
          <p><strong>bold</strong>
          <em>italic</em>
          <code>code</code>
          <a href="https://www.example.com">link</a>
          <img src="https://www.example.com/image.jpg" alt="image" /></p>
          <ul>
          <li>item1</li>
          <li>item2</li>
          </ul>
          
          """
          .trimIndent()
      Assertions.assertThat(actual).isEqualTo(expected)
    }
  }
}