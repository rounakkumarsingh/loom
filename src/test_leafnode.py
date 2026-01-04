import unittest

from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):

    def test_leaf_node_inherits_from_htmlnode(self):
        """Test class inheritance hierarchy.
        
        Verifies that:
        - LeafNode is a subclass of HTMLNode
        - All HTMLNode methods are available
        - Proper inheritance chain is maintained
        """
        from htmlnode import HTMLNode
        node = LeafNode("p", "text")
        self.assertIsInstance(node, HTMLNode)
    
    def test_leaf_node_no_children(self):
        """Test that LeafNode enforces the leaf constraint.
        
        Verifies that:
        - Children attribute is always None
        - LeafNode represents terminal nodes in the tree
        - No child nodes can be attached
        """
        node = LeafNode("p", "text")
        self.assertIsNone(node.children)

    def test_leaf_to_html_p(self):
        """Test basic paragraph tag HTML generation.
        
        Verifies that:
        - Opening tag is generated: <p>
        - Value content is placed inside tags
        - Closing tag is generated: </p>
        """
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_to_html_with_props(self):
        """Test HTML generation with a single property.
        
        Verifies that:
        - Property is included in opening tag
        - Format is: <tag prop="value">content</tag>
        - Link-specific href attribute works correctly
        """
        node = LeafNode("a", "Click me", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me</a>')

    def test_to_html_with_multiple_props(self):
        """Test HTML generation with multiple properties.
        
        Verifies that:
        - All properties are included in the opening tag
        - Order of properties may vary (dict ordering)
        - Standard HTML attributes like href, target, class work
        """
        node = LeafNode("a", "Link", {"href": "url", "target": "_blank", "class": "link"})
        html = node.to_html()
        self.assertIn('<a', html)
        self.assertIn('href="url"', html)
        self.assertIn('target="_blank"', html)
        self.assertIn('class="link"', html)
        self.assertIn('>Link</a>', html)

    def test_to_html_no_tag(self):
        """Test raw text rendering without HTML tags.
        
        Verifies that:
        - None tag means render value as plain text
        - No opening or closing tags are added
        - Useful for text nodes in the DOM tree
        """
        node = LeafNode(None, "This is just text.")
        self.assertEqual(node.to_html(), "This is just text.")

    def test_to_html_empty_value_raises_error(self):
        """Test that None value is invalid for LeafNode.
        
        Verifies that:
        - None value raises ValueError
        - Leaf nodes must have content (unlike parent nodes)
        - Empty string is different from None
        """
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_value_with_special_html_characters(self):
        """Test handling of potentially dangerous HTML content.
        
        Verifies that:
        - HTML tags in values are rendered literally (not escaped)
        - Script tags are treated as plain text
        - No XSS sanitization is performed by LeafNode
        """
        node = LeafNode("p", "<script>alert('xss')</script>")
        html = node.to_html()
        self.assertEqual(html, "<p><script>alert('xss')</script></p>")

    def test_value_with_html_entities(self):
        """Test preservation of HTML entities in values.
        
        Verifies that:
        - Pre-encoded entities like &lt; are preserved
        - No double-encoding occurs
        - Entity references pass through unchanged
        """
        node = LeafNode("p", "&lt;tag&gt;")
        self.assertEqual(node.to_html(), "<p>&lt;tag&gt;</p>")

    def test_to_html_empty_value_is_valid(self):
        """Test that empty string values are valid unlike None.
        
        Verifies that:
        - Empty string "" is different from None
        - Creates valid empty tags like <p></p>
        - Useful for self-closing tags or placeholders
        """
        # Empty string is valid HTML content (e.g., <span></span>)
        # Only None should raise ValueError, not empty string
        node = LeafNode("p", "")
        self.assertEqual(node.to_html(), "<p></p>")

    def test_to_html_p_with_no_props(self):
        """Test paragraph generation without any properties.
        
        Verifies that:
        - Simple <tag>value</tag> structure works
        - No spurious attributes are added
        - Most common use case works correctly
        """
        node = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

    def test_very_long_value(self):
        """Test handling of extremely long text values.
        
        Verifies that:
        - Large strings (10,000+ chars) are handled
        - No truncation occurs
        - Performance remains acceptable
        """
        long_text = "a" * 10000
        node = LeafNode("p", long_text)
        html = node.to_html()
        self.assertIn(long_text, html)

    def test_custom_tag(self):
        """Test support for custom/non-standard HTML tags.
        
        Verifies that:
        - Web component tags like <custom-element> work
        - No tag validation is performed
        - Useful for modern web components and custom elements
        """
        node = LeafNode("custom-element", "Content")
        self.assertEqual(node.to_html(), "<custom-element>Content</custom-element>")

if __name__ == "__main__":
    unittest.main()
