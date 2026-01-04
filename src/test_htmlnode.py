import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_multiple_props(self):
        """Test conversion of multiple properties to HTML attributes.
        
        Verifies that:
        - Multiple props are converted to space-separated attributes
        - Each attribute follows the format: key="value"
        - Leading space is included before attributes
        """
        node = HTMLNode(
            props={"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_props_to_html_with_single_prop(self):
        """Test conversion of a single property to HTML attribute.
        
        Verifies that:
        - Single prop is correctly formatted
        - Leading space is included
        - URL values are preserved exactly
        """
        node = HTMLNode(props={"href": "https://www.boot.dev"})
        self.assertEqual(node.props_to_html(), ' href="https://www.boot.dev"')

    def test_props_with_quotes_in_value(self):
        """Test handling of quotes within property values.
        
        Verifies that:
        - Double quotes in values are escaped as &quot;
        - The attribute value remains properly quoted
        - No XSS vulnerabilities are introduced
        """
        node = HTMLNode(props={"title": 'Say "hello"'})
        self.assertEqual(node.props_to_html(), ' "Say &quot;hello&quot;"')

    def test_props_with_empty_string_value(self):
        """Test that empty string values are valid and rendered.
        
        Verifies that:
        - Empty strings are different from None/missing props
        - Empty values produce key="" format
        - This is valid HTML for attributes like alt=""
        """
        node = HTMLNode(props={"alt": ""})
        self.assertEqual(node.props_to_html(), ' alt=""')

    def test_props_with_numeric_value(self):
        """Test automatic conversion of numeric values to strings.
        
        Verifies that:
        - Integer values are converted to strings
        - Multiple numeric props are handled correctly
        - The numeric values are properly quoted
        """
        node = HTMLNode(props={"width": 100, "height": 200})
        result = node.props_to_html()
        self.assertIn('width="100"', result)
        self.assertIn('height="200"', result)

    def test_props_with_style_attribute(self):
        """Test handling of CSS style attributes.
        
        Verifies that:
        - Complex style values with colons and semicolons work
        - Multiple CSS properties are preserved
        - Spacing in CSS is maintained
        """
        node = HTMLNode(props={"style": "color: red; background: blue; margin: 10px;"})
        self.assertEqual(
            node.props_to_html(),
            ' style="color: red; background: blue; margin: 10px;"'
        )

    def test_props_to_html_with_no_props(self):
        """Test handling when props parameter is None.
        
        Verifies that:
        - None props returns empty string
        - No errors are raised
        - No spurious whitespace is added
        """
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")
    
    def test_props_to_html_with_empty_props(self):
        """Test handling of empty props dictionary.
        
        Verifies that:
        - Empty dict {} is different from None
        - Empty dict also returns empty string
        - No iteration errors occur
        """
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_repr(self):
        """Test string representation of HTMLNode for debugging.
        
        Verifies that:
        - All constructor arguments are shown in repr
        - Format is: HTMLNode(tag, value, children, props)
        - Output is valid Python-like syntax
        """
        node = HTMLNode("p", "value", None, {"href": "https://www.boot.dev"})
        self.assertEqual(
            "HTMLNode(p, value, None, {'href': 'https://www.boot.dev'})", repr(node)
        )

if __name__ == "__main__":
    unittest.main()
