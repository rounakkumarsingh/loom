import unittest

from textnode import TextNode, TextType
from inline import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_delimiter_code(self):
        """
        Tests splitting a single node with a code block delimiter.
        """
        node = TextNode("This is text with a `code block` word", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PLAIN),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_bold(self):
        """
        Tests splitting a single node with a bold delimiter.
        """
        node = TextNode("This is text with a **bolded** word", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PLAIN),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_italic(self):
        """
        Tests splitting a single node with an italic delimiter.
        """
        node = TextNode("This is text with an *italic* word", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_split_nodes_unmatched_delimiter_raises_error(self):
        """
        Tests that an unmatched delimiter raises a ValueError.
        """
        node = TextNode("This is text with an *unmatched italic word", TextType.PLAIN)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "*", TextType.ITALIC)

    def test_split_multiple_delimiters_in_one_node(self):
        """
        Tests splitting a node with multiple pairs of the same delimiter.
        """
        node = TextNode("This is **bold** and this is **bold again**", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" and this is ", TextType.PLAIN),
                TextNode("bold again", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_non_text_node_is_passed_through(self):
        """
        Tests that a non-plain text node is passed through unchanged.
        """
        nodes = [
            TextNode("This is a bold node", TextType.BOLD),
            TextNode("This is an italic node", TextType.ITALIC),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertListEqual(nodes, new_nodes)

    def test_mixed_nodes_processed_correctly(self):
        """
        Tests a list with both PLAIN and other node types.
        """
        nodes = [
            TextNode("Some *italic* text", TextType.PLAIN),
            TextNode("This is a code block", TextType.CODE),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("Some ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.PLAIN),
                TextNode("This is a code block", TextType.CODE),
            ],
            new_nodes,
        )

    def test_delimiter_at_start_and_end(self):
        """
        Tests a node where the text is fully enclosed in delimiters.
        """
        node = TextNode("**bold word**", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("bold word", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_double_delimiter_creates_no_node(self):
        """
        Tests that back-to-back delimiters result in an empty string that is skipped.
        """
        node = TextNode("a **** b", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("a ", TextType.PLAIN),
                TextNode(" b", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_multiple_plain_nodes_are_split(self):
        """
        Tests splitting across multiple plain text nodes in a list.
        """
        nodes = [
            TextNode("Plain text, then ", TextType.PLAIN),
            TextNode("*italic* and more", TextType.PLAIN),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("Plain text, then ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and more", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_no_delimiter_in_node(self):
        """
        Tests that a node without the delimiter is returned unchanged.
        """
        node = TextNode("Just plain text.", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual([node], new_nodes)

    def test_delimiter_at_beginning(self):
        """
        Tests a node where the delimiter is at the start of the text.
        """
        node = TextNode("*italic* at the start", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("italic", TextType.ITALIC),
                TextNode(" at the start", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_delimiter_at_very_end(self):
        """
        Tests a node where the text ends with a closing delimiter.
        """
        node = TextNode("Text with *italic*", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("Text with ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_non_text_node_with_url_is_preserved(self):
        """
        Tests that a non-plain node with a URL is passed through unchanged.
        """
        nodes = [
            TextNode("link text", TextType.LINK, url="http://example.com"),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertListEqual(nodes, new_nodes)
        self.assertEqual(new_nodes[0].url, "http://example.com")

    def test_sequential_splitting(self):
        """
        Tests sequential splitting with different delimiters as a compound operation.
        """
        node = TextNode("This is **bold** and `code`", TextType.PLAIN)
        bold_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        final_nodes = split_nodes_delimiter(bold_nodes, "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.PLAIN),
                TextNode("code", TextType.CODE),
            ],
            final_nodes,
        )


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_images_single(self):
        text = "This is text with an ![image](https://example.com/image.png)"
        self.assertEqual(
            [("image", "https://example.com/image.png")],
            extract_markdown_images(text),
        )

    def test_extract_images_multiple(self):
        text = "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)"
        self.assertEqual(
            [
                (
                    "image",
                    "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
                ),
                (
                    "another",
                    "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png",
                ),
            ],
            extract_markdown_images(text),
        )

    def test_extract_images_no_images(self):
        text = "This is just text."
        self.assertEqual([], extract_markdown_images(text))

    def test_extract_images_is_not_link(self):
        text = "[link](https://example.com)"
        self.assertEqual([], extract_markdown_images(text))

    def test_extract_images_alt_with_spaces(self):
        text = "![alt text with spaces](url.png)"
        self.assertEqual(
            [("alt text with spaces", "url.png")], extract_markdown_images(text)
        )


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_links_single(self):
        text = "This is text with a [link](https://example.com)."
        self.assertEqual(
            [("link", "https://example.com")],
            extract_markdown_links(text),
        )

    def test_extract_links_multiple(self):
        text = "This is text with a [link](https_boot_dev) and [another link](https_google_com)"
        self.assertEqual(
            [("link", "https_boot_dev"), ("another link", "https_google_com")],
            extract_markdown_links(text),
        )

    def test_extract_links_no_links(self):
        text = "This is just text."
        self.assertEqual([], extract_markdown_links(text))

    def test_extract_links_ignores_images(self):
        text = "This text has a link [here](https://example.com) and an image ![here too](https://example.com/img.png)"
        self.assertEqual(
            [("here", "https://example.com")], extract_markdown_links(text)
        )


class TestSplitNodesImage(unittest.TestCase):
    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_image_single(self):
        node = TextNode(
            "![image](https://www.example.com/image.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("image", TextType.IMAGE, "https://www.example.com/image.png")],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("This is a node with no images.", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_image_at_start(self):
        node = TextNode("![alt text](url) some trailing text", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("alt text", TextType.IMAGE, "url"),
                TextNode(" some trailing text", TextType.PLAIN),
            ],
            new_nodes,
        )

    def test_image_at_end(self):
        node = TextNode("Some leading text ![alt text](url)", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Some leading text ", TextType.PLAIN),
                TextNode("alt text", TextType.IMAGE, "url"),
            ],
            new_nodes,
        )

    def test_non_text_node_unchanged(self):
        node = TextNode("![alt text](url)", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("alt text", TextType.IMAGE, "url")], new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_link(self):
        node = TextNode(
            "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://www.example.com"),
                TextNode(" and ", TextType.PLAIN),
                TextNode("another", TextType.LINK, "https://www.example.com/another"),
            ],
            new_nodes,
        )

    def test_split_link_single(self):
        node = TextNode(
            "[link](https://www.example.com)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://www.example.com")],
            new_nodes,
        )

    def test_no_links(self):
        node = TextNode("This node has no links.", TextType.PLAIN)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_ignores_image(self):
        node = TextNode(
            "This has a [link](https://boot.dev) but also an ![image](https://boot.dev/image.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This has a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(
                    " but also an ![image](https://boot.dev/image.png)",
                    TextType.PLAIN,
                ),
            ],
            new_nodes,
        )

    def test_non_text_node_unchanged_link(self):
        node = TextNode("[link](https://example.com)", TextType.ITALIC)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://example.com")], new_nodes
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.PLAIN),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.PLAIN),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_plain_text(self):
        text = "This is just plain text."
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("This is just plain text.", TextType.PLAIN)], nodes
        )

    def test_empty_string(self):
        text = ""
        nodes = text_to_textnodes(text)
        self.assertListEqual([], nodes)

    def test_only_bold(self):
        text = "**This is bold**"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is bold", TextType.BOLD)], nodes)

    def test_only_italic(self):
        text = "_This is italic_"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is italic", TextType.ITALIC)], nodes)

    def test_only_italic_with_no_flanking_whitespace(self):
        """Checks for flanking whitespace before '_' for rendering italic font. 
        Otherwise commonmark spec specifies it as plain text"""
           
        text = "my_variable_name"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("my_variable_name", TextType.PLAIN)], nodes)

    def test_only_italic_with_asterisk(self):
        """Text with single asterisk before and after is also treated as italics"""
           
        text="*italic word*"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("italic word", TextType.ITALIC)], nodes)

    def test_mismatched_delimiters_no_italics(self):
        """Mismatched delimiters don't create italics"""
           
        text = "*italics_"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_backslash_escapes_italics(self):
        """Backslash escapes italics markers"""
           
        text = r"This is \*not italicized\*"
        # The 'r' before "This is \*not emphasized\*" tells python that the backslash '\'
        # is not an escape sequence
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is *not italicized*", TextType.PLAIN)], nodes)
        # Should remain plain with literal asterisks

    def test_only_code(self):
        text = "`This is code`"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is code", TextType.CODE)], nodes)

    def test_code_span_with_backtick_inside(self):
        """Code span containing backtick uses double backticks"""
           
        text = "Use ``code with ` backtick``"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[1].node_type, TextType.CODE)
        self.assertEqual(nodes[1].text, "code with ` backtick")

    def test_only_link(self):
        text = "[a link](https://example.com)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("a link", TextType.LINK, "https://example.com")], nodes
        )

    def test_link_with_empty_url(self):
        """Links can have empty URLs"""
           
        text = "[link]()"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].node_type, TextType.LINK)
        self.assertEqual(nodes[0].url, "")

    def test_link_with_parentheses_in_url(self):
        """URLs can contain balanced parentheses"""
           
        text = "[link](url(with)parens)"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].url, "url(with)parens")

    def test_only_image(self):
        text = "![an image](https://example.com/img.png)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("an image", TextType.IMAGE, "https://example.com/img.png")],
            nodes,
        )

    def test_image_with_empty_alt(self):
        """Images can have empty alt text"""
        text = "![](image.png)"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].node_type, TextType.IMAGE)
        self.assertEqual(nodes[0].text, "")

    def test_invalid_markdown(self):
        text = "This has **unclosed bold"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_double_link(self):
        text = "[a link](https://example.com)[another link](https://another.com)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("a link", TextType.LINK, "https://example.com"),
                TextNode("another link", TextType.LINK, "https://another.com"),
            ],
            nodes,
        )

    def test_double_image(self):
        text = "![an image](https://example.com/img.png)![another image](https://another.com/img.png)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("an image", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(
                    "another image", TextType.IMAGE, "https://another.com/img.png"
                ),
            ],
            nodes,
        )


if __name__ == "__main__":
    unittest.main()
