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
