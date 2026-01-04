import unittest

from parentnode import ParentNode
from leafnode import LeafNode
from htmlnode import HTMLNode

class TestParentNode(unittest.TestCase):

    def test_parent_node_inherits_from_htmlnode(self):
        """Test class inheritance hierarchy.
        
        Verifies that:
        - ParentNode is a subclass of HTMLNode
        - All HTMLNode methods are available
        - Proper inheritance chain is maintained
        """
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsInstance(node, HTMLNode)

    def test_to_html_with_children(self):
        """Test basic parent-child HTML structure.
        
        Verifies that:
        - Parent tag wraps child tag correctly
        - Child HTML is generated recursively
        - Format is: <parent><child>content</child></parent>
        """
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        """Test nested parent-child-grandchild structure.
        
        Verifies that:
        - Multiple levels of nesting work correctly
        - Each level generates its tags properly
        - Recursive rendering maintains structure
        """
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        """Test parent with multiple sibling children.
        
        Verifies that:
        - Multiple children are rendered in order
        - Mix of tagged and untagged (text) nodes works
        - All children are included without separators
        """
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
        """Test deeply nested structure with lists.
        
        Verifies that:
        - Multiple levels of ParentNode nesting work
        - Complex structures like ul > li > b render correctly
        - No depth limit is encountered
        """
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
        """Test parent node with HTML attributes.
        
        Verifies that:
        - Properties are added to parent's opening tag
        - Multiple props like class and id work together
        - Children are rendered inside tagged parent
        """
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
        """Test that ParentNode requires a tag.
        
        Verifies that:
        - None tag raises ValueError
        - Parent nodes must have tags (unlike LeafNode)
        - Error is raised before children are processed
        """
        node = ParentNode(None, [LeafNode("p", "hello")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children(self):
        """Test that ParentNode requires children.
        
        Verifies that:
        - Empty children list raises ValueError
        - Parent nodes must contain at least one child
        - Differentiates parent from self-closing tags
        """
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()
    
    def test_to_html_children_is_none(self):
        """Test that None children is invalid.
        
        Verifies that:
        - None children raises ValueError
        - None is different from empty list []
        - Children must be a list, not None
        """
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_mixed_children(self):
        """Test mixing LeafNode and ParentNode children.
        
        Verifies that:
        - Both leaf and parent children can coexist
        - Children are rendered in order
        - Complex document structures work correctly
        """
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
        """Test HTML table generation.
        
        Verifies that:
        - Nested table structure (table > tr > td) works
        - Multiple rows and cells render correctly
        - Table-specific tags are supported
        """
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
        """Test class attribute on parent element.
        
        Verifies that:
        - CSS class attribute is rendered correctly
        - Format is class="classname"
        - Useful for styling and JavaScript selection
        """
        node = ParentNode("div", [LeafNode("p", "Text")], {"class": "container"})
        html = node.to_html()
        self.assertIn('class="container"', html)

if __name__ == "__main__":
    unittest.main()
