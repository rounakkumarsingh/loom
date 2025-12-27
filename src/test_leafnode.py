import unittest

from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):

    def test_leaf_node_inherits_from_htmlnode(self):
        """LeafNode should inherit from HTMLNode"""
        from htmlnode import HTMLNode
        node = LeafNode("p", "text")
        self.assertIsInstance(node, HTMLNode)
    
    def test_leaf_node_no_children(self):
        """LeafNode should always have None children"""
        node = LeafNode("p", "text")
        self.assertIsNone(node.children)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_to_html_with_props(self):
        node = LeafNode("a", "Click me", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me</a>')

    def test_to_html_with_multiple_props(self):
        """HTML with multiple properties"""
        node = LeafNode("a", "Link", {"href": "url", "target": "_blank", "class": "link"})
        html = node.to_html()
        self.assertIn('<a', html)
        self.assertIn('href="url"', html)
        self.assertIn('target="_blank"', html)
        self.assertIn('class="link"', html)
        self.assertIn('>Link</a>', html)

    def test_to_html_no_tag(self):
        node = LeafNode(None, "This is just text.")
        self.assertEqual(node.to_html(), "This is just text.")

    def test_to_html_empty_value_raises_error(self):
        """None value should raise ValueError"""
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_value_with_special_html_characters(self):
        """Value with HTML special characters"""
        node = LeafNode("p", "<script>alert('xss')</script>")
        html = node.to_html()
        self.assertEqual(html, "<p><script>alert('xss')</script></p>")

    def test_value_with_html_entities(self):
        """Value with HTML entities"""
        node = LeafNode("p", "&lt;tag&gt;")
        self.assertEqual(node.to_html(), "<p>&lt;tag&gt;</p>")

    def test_to_html_empty_value_is_valid(self):
        # Empty string is valid HTML content (e.g., <span></span>)
        # Only None should raise ValueError, not empty string
        node = LeafNode("p", "")
        self.assertEqual(node.to_html(), "<p></p>")

    def test_to_html_p_with_no_props(self):
        node = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

    def test_very_long_value(self):
        """Very long value string"""
        long_text = "a" * 10000
        node = LeafNode("p", long_text)
        html = node.to_html()
        self.assertIn(long_text, html)

    def test_custom_tag(self):
        """Custom/unusual tag names"""
        node = LeafNode("custom-element", "Content")
        self.assertEqual(node.to_html(), "<custom-element>Content</custom-element>")

if __name__ == "__main__":
    unittest.main()
