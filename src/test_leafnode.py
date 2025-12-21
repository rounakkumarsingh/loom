import unittest

from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_to_html_with_props(self):
        node = LeafNode("a", "Click me", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me</a>')

    def test_to_html_no_tag(self):
        node = LeafNode(None, "This is just text.")
        self.assertEqual(node.to_html(), "This is just text.")

    def test_to_html_empty_value_is_valid(self):
        # Empty string is valid HTML content (e.g., <span></span>)
        # Only None should raise ValueError, not empty string
        node = LeafNode("p", "")
        self.assertEqual(node.to_html(), "<p></p>")

    def test_to_html_p_with_no_props(self):
        node = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

if __name__ == "__main__":
    unittest.main()
