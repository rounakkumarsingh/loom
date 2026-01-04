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


# ============================================================================
# DELIMITER PARSING TESTS
# ============================================================================

class TestDelimiterParsing(unittest.TestCase):
    """Tests for splitting text nodes by delimiters (bold, italic, code)."""

    def test_split_nodes_delimiter_code(self):
        """Test splitting a single node with a code block delimiter.
        
        Verifies that:
        - Code blocks enclosed in ` are recognized
        - Text is split into PLAIN and CODE nodes
        - Content order is preserved
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
        """Test splitting a single node with a bold delimiter.
        
        Verifies that:
        - Bold text enclosed in ** is recognized
        - Text is split into PLAIN and BOLD nodes
        - Double asterisks are consumed, not included
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
        """Test splitting a single node with an italic delimiter.
        
        Verifies that:
        - Italic text enclosed in * is recognized
        - Text is split into PLAIN and ITALIC nodes
        - Single asterisks are consumed, not included
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
        """Test that an unmatched delimiter raises a ValueError.
        
        Verifies that:
        - Opening delimiter without closing raises error
        - Invalid markdown is not silently accepted
        """
        node = TextNode("This is text with an *unmatched italic word", TextType.PLAIN)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "*", TextType.ITALIC)

    def test_split_multiple_delimiters_in_one_node(self):
        """Test splitting a node with multiple pairs of the same delimiter.
        
        Verifies that:
        - Multiple delimiter pairs are all processed
        - Pairs are matched left-to-right
        - Each pair creates separate formatted nodes
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
        """Test that a non-plain text node is passed through unchanged.
        
        Verifies that:
        - BOLD, ITALIC, CODE nodes are not split
        - Non-PLAIN nodes pass through unchanged
        """
        nodes = [
            TextNode("This is a bold node", TextType.BOLD),
            TextNode("This is an italic node", TextType.ITALIC),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertListEqual(nodes, new_nodes)

    def test_mixed_nodes_processed_correctly(self):
        """Test a list with both PLAIN and other node types.
        
        Verifies that:
        - PLAIN nodes are split by delimiter
        - Non-PLAIN nodes remain unchanged
        - Order of nodes is preserved
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
        """Test a node where the text is fully enclosed in delimiters.
        
        Verifies that:
        - Entire text can be enclosed in delimiters
        - Single formatted node is created
        - No PLAIN nodes are generated
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
        """Test that back-to-back delimiters result in an empty string that is skipped.
        
        Verifies that:
        - Adjacent delimiter pairs with no content
        - Results in empty string that is skipped
        - No empty nodes are created
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
        """Test splitting across multiple plain text nodes in a list.
        
        Verifies that:
        - Each PLAIN node is processed independently
        - Splitting works across multiple list items
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
        """Test that a node without the delimiter is returned unchanged.
        
        Verifies that:
        - Nodes without target delimiter are not modified
        - Original node is returned in list
        """
        node = TextNode("Just plain text.", TextType.PLAIN)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual([node], new_nodes)

    def test_delimiter_at_beginning(self):
        """Test a node where the delimiter is at the start of the text.
        
        Verifies that:
        - Delimiters at start create no leading PLAIN node
        - Formatted node is first in result
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
        """Test a node where the text ends with a closing delimiter.
        
        Verifies that:
        - Delimiters at end create no trailing PLAIN node
        - Formatted node is last in result
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
        """Test that a non-plain node with a URL is passed through unchanged.
        
        Verifies that:
        - Nodes with URLs pass through unchanged
        - URL attribute is not lost during processing
        """
        nodes = [
            TextNode("link text", TextType.LINK, url="http://example.com"),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertListEqual(nodes, new_nodes)
        self.assertEqual(new_nodes[0].url, "http://example.com")

    def test_sequential_splitting(self):
        """Test sequential splitting with different delimiters as a compound operation.
        
        Verifies that:
        - Multiple delimiter types can be applied in sequence
        - First pass handles one delimiter type
        - Second pass handles another delimiter type
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


# ============================================================================
# IMAGE EXTRACTION AND SPLITTING TESTS
# ============================================================================

class TestExtractMarkdownImages(unittest.TestCase):
    """Tests for extracting image references from markdown text."""

    def test_extract_images_single(self):
        """Test extracting a single image reference.
        
        Verifies that:
        - Image syntax ![alt](url) is recognized
        - Returns list of (alt_text, url) tuples
        """
        text = "This is text with an ![image](https://example.com/image.png)"
        self.assertEqual(
            [("image", "https://example.com/image.png")],
            extract_markdown_images(text),
        )

    def test_extract_images_multiple(self):
        """Test extracting multiple image references.
        
        Verifies that:
        - Multiple images in text are all extracted
        - Images are returned in order of appearance
        """
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
        """Test text without images returns empty list.
        
        Verifies that:
        - Plain text returns empty list
        - No false positives on non-image text
        """
        text = "This is just text."
        self.assertEqual([], extract_markdown_images(text))

    def test_extract_images_is_not_link(self):
        """Test that regular links are not detected as images.
        
        Verifies that:
        - Link syntax [text](url) is not matched
        - Only image syntax ![text](url) is matched
        """
        text = "[link](https://example.com)"
        self.assertEqual([], extract_markdown_images(text))

    def test_extract_images_alt_with_spaces(self):
        """Test alt text can contain spaces.
        
        Verifies that:
        - Alt text with multiple words works
        - Spaces in alt text are preserved
        """
        text = "![alt text with spaces](url.png)"
        self.assertEqual(
            [("alt text with spaces", "url.png")], extract_markdown_images(text)
        )


class TestSplitNodesImage(unittest.TestCase):
    """Tests for splitting text nodes containing image references."""

    def test_split_image(self):
        """Test splitting text with multiple images.
        
        Verifies that:
        - Text is split at each image reference
        - IMAGE nodes are created with correct alt and URL
        - Plain text between images is preserved
        """
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
        """Test text containing only an image reference.
        
        Verifies that:
        - Image-only text creates single IMAGE node
        - No PLAIN nodes are created
        """
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
        """Test that nodes without images pass through unchanged.
        
        Verifies that:
        - Text without images is not modified
        - Original node is returned unchanged
        """
        node = TextNode("This is a node with no images.", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_image_at_start(self):
        """Test image reference at beginning of text.
        
        Verifies that:
        - Leading image creates no leading PLAIN node
        - Trailing text becomes PLAIN node
        """
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
        """Test image reference at end of text.
        
        Verifies that:
        - Trailing image creates no trailing PLAIN node
        - Leading text becomes PLAIN node
        """
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
        """Test that even non-PLAIN nodes are processed for images.
        
        Verifies that:
        - Node type doesn't prevent image extraction
        - Images are detected regardless of node type
        """
        node = TextNode("![alt text](url)", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("alt text", TextType.IMAGE, "url")], new_nodes)


# ============================================================================
# LINK EXTRACTION AND SPLITTING TESTS
# ============================================================================

class TestExtractMarkdownLinks(unittest.TestCase):
    """Tests for extracting link references from markdown text."""

    def test_extract_links_single(self):
        """Test extracting a single link reference.
        
        Verifies that:
        - Link syntax [text](url) is recognized
        - Returns list of (link_text, url) tuples
        """
        text = "This is text with a [link](https://example.com)."
        self.assertEqual(
            [("link", "https://example.com")],
            extract_markdown_links(text),
        )

    def test_extract_links_multiple(self):
        """Test extracting multiple link references.
        
        Verifies that:
        - Multiple links in text are all extracted
        - Links are returned in order of appearance
        """
        text = "This is text with a [link](https_boot_dev) and [another link](https_google_com)"
        self.assertEqual(
            [("link", "https_boot_dev"), ("another link", "https_google_com")],
            extract_markdown_links(text),
        )

    def test_extract_links_no_links(self):
        """Test text without links returns empty list.
        
        Verifies that:
        - Plain text returns empty list
        - No false positives on non-link text
        """
        text = "This is just text."
        self.assertEqual([], extract_markdown_links(text))

    def test_extract_links_ignores_images(self):
        """Test that image syntax is not detected as links.
        
        Verifies that:
        - Image syntax ![text](url) is not matched
        - Only link syntax [text](url) is matched
        """
        text = "This text has a link [here](https://example.com) and an image ![here too](https://example.com/img.png)"
        self.assertEqual(
            [("here", "https://example.com")], extract_markdown_links(text)
        )


class TestSplitNodesLink(unittest.TestCase):
    """Tests for splitting text nodes containing link references."""

    def test_split_link(self):
        """Test splitting text with multiple links.
        
        Verifies that:
        - Text is split at each link reference
        - LINK nodes are created with correct text and URL
        - Plain text between links is preserved
        """
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
        """Test text containing only a link reference.
        
        Verifies that:
        - Link-only text creates single LINK node
        - No PLAIN nodes are created
        """
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
        """Test that nodes without links pass through unchanged.
        
        Verifies that:
        - Text without links is not modified
        - Original node is returned unchanged
        """
        node = TextNode("This node has no links.", TextType.PLAIN)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_ignores_image(self):
        """Test that image references are not processed as links.
        
        Verifies that:
        - Only [text](url) is processed, not ![text](url)
        - Image syntax remains in plain text
        """
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
        """Test that even non-PLAIN nodes are processed for links.
        
        Verifies that:
        - Node type doesn't prevent link extraction
        - Links are detected regardless of node type
        """
        node = TextNode("[link](https://example.com)", TextType.ITALIC)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://example.com")], new_nodes
        )


# ============================================================================
# COMPLETE TEXT-TO-NODES CONVERSION TESTS
# ============================================================================

class TestTextToTextNodes(unittest.TestCase):
    """Tests for complete text-to-nodes conversion with all inline elements."""

    def test_text_to_textnodes_example(self):
        """Test text containing all inline markdown types.
        
        Verifies that:
        - Bold, italic, code, images, and links are all detected
        - Multiple formatting types work together
        - Processing order preserves structure
        """
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
        """Test text with no markdown formatting.
        
        Verifies that:
        - Plain text returns single PLAIN node
        - No formatting is falsely detected
        """
        text = "This is just plain text."
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("This is just plain text.", TextType.PLAIN)], nodes
        )

    def test_empty_string(self):
        """Test empty string returns empty list.
        
        Verifies that:
        - Empty input is handled gracefully
        - No nodes are created for empty string
        """
        text = ""
        nodes = text_to_textnodes(text)
        self.assertListEqual([], nodes)

    def test_only_bold(self):
        """Test text that is entirely bold.
        
        Verifies that:
        - Fully bold text creates single BOLD node
        - No PLAIN nodes are created
        """
        text = "**This is bold**"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is bold", TextType.BOLD)], nodes)

    def test_only_italic(self):
        """Test italic using underscore syntax.
        
        Verifies that:
        - Underscore _text_ creates italic
        - Fully italic text creates single ITALIC node
        """
        text = "_This is italic_"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is italic", TextType.ITALIC)], nodes)

    def test_only_italic_with_no_flanking_whitespace(self):
        """Test underscores that don't indicate italic formatting.
        
        Verifies that:
        - Underscores without flanking whitespace are literal
        - Variable names like my_var_name remain plain
        - CommonMark flanking rules are respected
        """
        text = "my_variable_name"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("my_variable_name", TextType.PLAIN)], nodes)

    def test_only_italic_with_asterisk(self):
        """Test italic using single asterisk syntax.
        
        Verifies that:
        - Single asterisk *text* creates italic
        - Both underscore and asterisk work for italic
        """
        text="*italic word*"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("italic word", TextType.ITALIC)], nodes)

    def test_mismatched_delimiters_no_italics(self):
        """Test that mismatched italic markers raise error.
        
        Verifies that:
        - Opening * with closing _ (or vice versa) raises error
        - Delimiter pairs must match
        """
        text = "*italics_"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_backslash_escapes_italics(self):
        """Test backslash-escaped formatting markers.
        
        Verifies that:
        - Backslash before marker prevents formatting
        - Escaped markers appear as literal characters
        - Backslash is consumed in output
        """
        text = r"This is \*not italicized\*"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is *not italicized*", TextType.PLAIN)], nodes)

    def test_only_code(self):
        """Test text that is entirely code.
        
        Verifies that:
        - Fully code text creates single CODE node
        - No PLAIN nodes are created
        """
        text = "`This is code`"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is code", TextType.CODE)], nodes)

    def test_code_span_with_backtick_inside(self):
        """Test code span containing a backtick character.
        
        Verifies that:
        - Double backticks allow single backtick inside
        - Inner backtick is preserved literally
        """
        text = "Use ``code with ` backtick``"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[1].node_type, TextType.CODE)
        self.assertEqual(nodes[1].text, "code with ` backtick")

    def test_only_link(self):
        """Test text that is only a link.
        
        Verifies that:
        - Link-only text creates single LINK node
        - URL is captured correctly
        """
        text = "[a link](https://example.com)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("a link", TextType.LINK, "https://example.com")], nodes
        )

    def test_link_with_empty_url(self):
        """Test links can have empty URL field.
        
        Verifies that:
        - Empty parentheses () are valid
        - LINK node is created with empty URL
        """
        text = "[link]()"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].node_type, TextType.LINK)
        self.assertEqual(nodes[0].url, "")

    def test_link_with_parentheses_in_url(self):
        """Test URLs can contain balanced parentheses.
        
        Verifies that:
        - Parentheses inside URL are preserved
        - Balanced parens don't break URL parsing
        """
        text = "[link](url(with)parens)"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].url, "url(with)parens")

    def test_only_image(self):
        """Test text that is only an image.
        
        Verifies that:
        - Image-only text creates single IMAGE node
        - Alt text and URL are captured correctly
        """
        text = "![an image](https://example.com/img.png)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("an image", TextType.IMAGE, "https://example.com/img.png")],
            nodes,
        )

    def test_image_with_empty_alt(self):
        """Test images can have empty alt text.
        
        Verifies that:
        - Empty alt text ![]() is valid
        - IMAGE node is created with empty text
        """
        text = "![](image.png)"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].node_type, TextType.IMAGE)
        self.assertEqual(nodes[0].text, "")

    def test_invalid_markdown(self):
        """Test that unclosed bold delimiter raises error.
        
        Verifies that:
        - Opening ** without closing ** raises ValueError
        - Malformed markdown is not silently accepted
        """
        text = "This has **unclosed bold"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_double_link(self):
        """Test two links with no text between them.
        
        Verifies that:
        - Adjacent links are both recognized
        - No PLAIN node is created between them
        """
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
        """Test two images with no text between them.
        
        Verifies that:
        - Adjacent images are both recognized
        - No PLAIN node is created between them
        """
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