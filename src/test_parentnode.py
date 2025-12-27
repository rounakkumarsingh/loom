import unittest

from parentnode import ParentNode
from leafnode import LeafNode
from htmlnode import HTMLNode

class TestParentNode(unittest.TestCase):

    def test_parent_node_inherits_from_htmlnode(self):
        """ParentNode should inherit from HTMLNode"""
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsInstance(node, HTMLNode)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        node = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text again"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><b>Bold text</b>Normal text<i>italic text</i>Normal text again</div>",
        )

    def test_to_html_with_deep_nesting(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "ul",
                    [
                        ParentNode("li", [LeafNode("b", "item 1")]),
                        ParentNode("li", [LeafNode("i", "item 2")]),
                    ]
                )
            ]
        )
        self.assertEqual(
            node.to_html(),
            "<div><ul><li><b>item 1</b></li><li><i>item 2</i></li></ul></div>"
        )

    def test_to_html_with_props(self):
        node = ParentNode(
            "div",
            [LeafNode("b", "Bold text")],
            {"class": "my-div", "id": "main-div"}
        )
        self.assertEqual(
            node.to_html(),
            '<div class="my-div" id="main-div"><b>Bold text</b></div>'
        )

    def test_to_html_no_tag(self):
        node = ParentNode(None, [LeafNode("p", "hello")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()
    
    def test_to_html_children_is_none(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_mixed_children(self):
        """Parent with both leaf and parent children"""
        children = [
            LeafNode("h1", "Title"),
            LeafNode("p", "Intro"),
            ParentNode("ul", [
                LeafNode("li", "Item 1"),
                LeafNode("li", "Item 2")
            ]),
            LeafNode("p", "Conclusion")
        ]
        parent = ParentNode("div", children)
        html = parent.to_html()
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<ul>", html)
        self.assertIn("<li>Item 1</li>", html)

    def test_table_structure(self):
        """Table structure"""
        node = ParentNode("table", [
            ParentNode("tr", [
                LeafNode("td", "Cell 1"),
                LeafNode("td", "Cell 2")
            ]),
            ParentNode("tr", [
                LeafNode("td", "Cell 3"),
                LeafNode("td", "Cell 4")
            ])
        ])
        html = node.to_html()
        self.assertIn("<table>", html)
        self.assertIn("<tr>", html)
        self.assertIn("<td>Cell 1</td>", html)

    def test_props_with_class(self):
        """Props with class attribute"""
        node = ParentNode("div", [LeafNode("p", "Text")], {"class": "container"})
        html = node.to_html()
        self.assertIn('class="container"', html)

if __name__ == "__main__":
    unittest.main()
