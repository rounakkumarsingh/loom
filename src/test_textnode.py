
import unittest

from textnode import (
    TextNode,
    TextType,
    text_node_to_html_node,
)
from leafnode import LeafNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        """Test equality of TextNodes with identical content.
        
        Verifies that:
        - Two nodes with same text and type are equal
        - __eq__ method is properly implemented
        - URL defaults don't affect equality
        """
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        """Test inequality when text content differs.
        
        Verifies that:
        - Nodes with different text are not equal
        - Even with same type, different text causes inequality
        - Comparison is content-aware
        """
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_url(self):
        """Test inequality when URL differs.
        
        Verifies that:
        - Nodes with different URLs are not equal
        - Presence vs absence of URL matters
        - URL is part of equality comparison
        """
        node = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_type(self):
        """Test inequality when TextType differs.
        
        Verifies that:
        - Nodes with different types are not equal
        - Even with same text, different type causes inequality
        - Type is a key component of equality
        """
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_repr(self):
        """Test string representation for debugging.
        
        Verifies that:
        - All attributes are shown in repr output
        - Format is: TextNode(text, TYPE, url)
        - Useful for debugging and logging
        """
        node = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        self.assertEqual(
            repr(node), "TextNode(This is a text node, BOLD, https://www.boot.dev)"
        )


class TestTextNodeToHTML(unittest.TestCase):
    def test_plain(self):
        """Test conversion of plain text to HTML.
        
        Verifies that:
        - PLAIN type creates LeafNode without tag
        - Text content is preserved exactly
        - No formatting tags are added
        """
        node = TextNode("This is a text node", TextType.PLAIN)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        """Test conversion of bold text to HTML.
        
        Verifies that:
        - BOLD type creates LeafNode with 'b' tag
        - Text is wrapped in <b></b> tags
        - Follows HTML5 bold formatting convention
        """
        node = TextNode("This is a bold node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node")

    def test_italic(self):
        """Test conversion of italic text to HTML.
        
        Verifies that:
        - ITALIC type creates LeafNode with 'i' tag
        - Text is wrapped in <i></i> tags
        - Follows HTML5 italic formatting convention
        """
        node = TextNode("This is an italic node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node")

    def test_code(self):
        """Test conversion of code text to HTML.
        
        Verifies that:
        - CODE type creates LeafNode with 'code' tag
        - Text is wrapped in <code></code> tags
        - Inline code formatting is applied
        """
        node = TextNode("This is a code node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_link(self):
        """Test conversion of link text to HTML anchor.
        
        Verifies that:
        - LINK type creates LeafNode with 'a' tag
        - href property is set from URL parameter
        - Link text becomes the anchor content
        - Format is: <a href="url">text</a>
        """
        node = TextNode("This is a link node", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node")
        self.assertEqual(html_node.props, {"href": "https://www.boot.dev"})

    def test_link_no_url(self):
        """Test that link without URL raises error.
        
        Verifies that:
        - LINK type without URL is invalid
        - Accessing props on incomplete link raises ValueError
        - Enforces that links must have destinations
        - Follows CommonMark spec for links
        """
        node = TextNode("This is a link node without url", TextType.LINK)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node without url")
        with self.assertRaises(ValueError):
            html_node.props
        # Empty links are not rendered as links in commonmark spec

    def test_image(self):
        """Test conversion of image reference to HTML img tag.
        
        Verifies that:
        - IMAGE type creates LeafNode with 'img' tag
        - src property is set from URL parameter
        - alt property is set from text content
        - Value is empty string (img is self-closing)
        - Format is: <img src="url" alt="text">
        """
        node = TextNode(
            "alt text for image", TextType.IMAGE, "https://www.boot.dev/image.png"
        )
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        # Images use 'src' attribute, not 'href'
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev/image.png", "alt": "alt text for image"},
        )


if __name__ == "__main__":
    unittest.main()
