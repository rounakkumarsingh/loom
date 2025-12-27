import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_multiple_props(self):
        node = HTMLNode(
            props={"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_props_to_html_with_single_prop(self):
        node = HTMLNode(props={"href": "https://www.boot.dev"})
        self.assertEqual(node.props_to_html(), ' href="https://www.boot.dev"')

    def test_props_with_quotes_in_value(self):
        """Props with quotes in values"""
        node = HTMLNode(props={"title": 'Say "hello"'})
        self.assertEqual(node.props_to_html(), ' "Say &quot;hello&quot;"')

    def test_props_with_empty_string_value(self):
        """Props can have empty string values"""
        node = HTMLNode(props={"alt": ""})
        self.assertEqual(node.props_to_html(), ' alt=""')

    def test_props_with_numeric_value(self):
        """Props with numeric values are converted to strings"""
        node = HTMLNode(props={"width": 100, "height": 200})
        result = node.props_to_html()
        self.assertIn('width="100"', result)
        self.assertIn('height="200"', result)

    def test_props_with_style_attribute(self):
        """Props with CSS style attribute"""
        node = HTMLNode(props={"style": "color: red; background: blue; margin: 10px;"})
        self.assertEqual(
            node.props_to_html(),
            ' style="color: red; background: blue; margin: 10px;"'
        )

    def test_props_to_html_with_no_props(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")
    
    def test_props_to_html_with_empty_props(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_repr(self):
        node = HTMLNode("p", "value", None, {"href": "https://www.boot.dev"})
        self.assertEqual(
            "HTMLNode(p, value, None, {'href': 'https://www.boot.dev'})", repr(node)
        )

if __name__ == "__main__":
    unittest.main()
