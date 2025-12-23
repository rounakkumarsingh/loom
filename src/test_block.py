import unittest
from block import markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node


class TestBlockFunctions(unittest.TestCase):
    # Existing tests for markdown_to_blocks

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """

This is **bolded** paragraph



This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items

"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_mixed_line_endings(self):
        md = (
            "This is **bolded** paragraph\r\n\r\n"
            "This is another paragraph with _italic_ text and `code` here\n"
            "This is the same paragraph on a new line\r\n\r\n"
            "- This is a list\n"
            "- with items\r\n"
        )

        blocks = markdown_to_blocks(md)

        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\n"
                "This is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_single_block(self):
        md = "This is just one block."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is just one block."])

    def test_strip_whitespace(self):
        md = "  \n\n  block1  \n\n  block2  \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["block1", "block2"])

    def test_empty_input(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_only_whitespace(self):
        md = "   \n\n   \n "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    # New tests for block_to_block_type

    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Heading 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Heading 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)
        self.assertEqual(
            block_to_block_type(" #Not a heading"), BlockType.PARAGRAPH
        )  # leading space
        self.assertEqual(
            block_to_block_type("##Heading 2"), BlockType.PARAGRAPH
        )  # Missing space
        self.assertEqual(
            block_to_block_type("####### Heading 7"), BlockType.PARAGRAPH
        )  # Too many #
        self.assertEqual(
            block_to_block_type("#Not a heading"), BlockType.PARAGRAPH
        )  # Not a valid heading pattern

    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```code\nblock\n```"), BlockType.CODE)
        self.assertEqual(
            block_to_block_type("```\nprint('hello')\n```"), BlockType.CODE
        )
        self.assertEqual(block_to_block_type("```  \nsome code\n  ```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("```code block\n\n```"), BlockType.CODE)
        self.assertEqual(
            block_to_block_type("```\n```"), BlockType.CODE
        )  # Empty code block
        # Changed this test to reflect the actual behavior of the provided regex
        self.assertEqual(
            block_to_block_type("```python\nprint('hi')\n```"), BlockType.CODE
        )  # Language specifier is included in the match
        self.assertEqual(block_to_block_type("code block```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```code block"), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("> Line 1\n> Line 2"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">  indented quote"), BlockType.QUOTE)
        # These tests are based on the assignment, which expects these to be QUOTE
        # The provided block.py code currently classifies ">" and ">\n> " as PARAGRAPH
        self.assertEqual(
            block_to_block_type("> "), BlockType.QUOTE
        )  # Single empty quote line
        self.assertEqual(
            block_to_block_type("> \n> "), BlockType.QUOTE
        )  # Empty quote lines
        self.assertEqual(
            block_to_block_type("> Line 1\nLine 2"), BlockType.PARAGRAPH
        )  # Missing '>' on one line
        self.assertEqual(
            block_to_block_type("This is not > a quote"), BlockType.PARAGRAPH
        )

    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(
            block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST
        )
        self.assertEqual(
            block_to_block_type("- Another item"), BlockType.UNORDERED_LIST
        )
        self.assertEqual(
            block_to_block_type("-   indented item"), BlockType.UNORDERED_LIST
        )
        # These tests are based on the assignment, which expects these to be UNORDERED_LIST
        # The provided block.py code currently classifies "-" and "- \n- " as PARAGRAPH
        self.assertEqual(
            block_to_block_type("- "), BlockType.UNORDERED_LIST
        )  # Single empty list item
        self.assertEqual(
            block_to_block_type("- \n- "), BlockType.UNORDERED_LIST
        )  # Empty list items
        self.assertEqual(
            block_to_block_type("- Item 1\nItem 2"), BlockType.PARAGRAPH
        )  # Missing '-' on one line
        self.assertEqual(block_to_block_type("Not - a list item"), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST
        )
        self.assertEqual(block_to_block_type("1. Item"), BlockType.ORDERED_LIST)
        self.assertEqual(
            block_to_block_type("1. Item 1\n2. Item 2\n3. Item 3"),
            BlockType.ORDERED_LIST,
        )
        self.assertEqual(
            block_to_block_type("1. Item 1\n2.Item 2"), BlockType.PARAGRAPH
        )  # Missing space after '.'
        self.assertEqual(
            block_to_block_type("1. Item 1\n3. Item 2"), BlockType.PARAGRAPH
        )  # Non-sequential numbers
        self.assertEqual(
            block_to_block_type("2. Item 1\n3. Item 2"), BlockType.PARAGRAPH
        )  # Starting number not 1
        self.assertEqual(
            block_to_block_type("1 Item 1\n2. Item 2"), BlockType.PARAGRAPH
        )  # Missing '.'
        self.assertEqual(
            block_to_block_type("1. Ordered\n- Unordered"), BlockType.PARAGRAPH
        )  # Mixed list types
        self.assertEqual(
            block_to_block_type("1. Item 1\n1. Item 2"), BlockType.PARAGRAPH
        )  # Repeated number

    def test_block_to_block_type_paragraph(self):
        self.assertEqual(
            block_to_block_type("This is a normal paragraph."), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("A paragraph with\nmultiple lines."),
            BlockType.PARAGRAPH,
        )
        self.assertEqual(block_to_block_type("Just some text."), BlockType.PARAGRAPH)
        self.assertEqual(
            block_to_block_type("A line with # but not a heading"), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("A line with - but not a list"), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("A line with > but not a quote"), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("A line with 1. but not an ordered list"),
            BlockType.PARAGRAPH,
        )
        # This test is based on the assignment, which expects empty string to be PARAGRAPH
        # The provided block.py code currently classifies "" as QUOTE
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)  # Empty string
        self.assertEqual(
            block_to_block_type("   "), BlockType.PARAGRAPH
        )  # Whitespace only string

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


if __name__ == "__main__":
    unittest.main()
