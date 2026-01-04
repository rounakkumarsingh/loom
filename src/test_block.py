import unittest
from block import markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node


class TestBlockFunctions(unittest.TestCase):
    # Existing tests for markdown_to_blocks

    def test_markdown_to_blocks(self):
        """Test basic block splitting functionality.
        
        Verifies that:
        - Multiple blocks separated by blank lines are correctly identified
        - Content within blocks is preserved including newlines
        - Markdown formatting within blocks is not processed
        """
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
        """Test handling of multiple consecutive newlines.
        
        Verifies that:
        - Multiple blank lines (2+) are treated as block separators
        - Leading and trailing newlines are ignored
        - Block content is preserved regardless of surrounding whitespace
        """
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
        """Test cross-platform line ending compatibility.
        
        Verifies that:
        - CRLF (\\r\\n) line endings are handled correctly
        - LF (\\n) line endings are handled correctly
        - Mixed line endings in the same document work properly
        - Block separation works regardless of line ending type
        """
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
        """Test document with no block separators.
        
        Verifies that:
        - A single block without blank lines returns one block
        - The content is preserved exactly as written
        """
        md = "This is just one block."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is just one block."])

    def test_strip_whitespace(self):
        """Test whitespace trimming behavior.
        
        Verifies that:
        - Leading whitespace is stripped from blocks
        - Trailing whitespace is stripped from blocks
        - Internal whitespace within blocks is preserved
        """        
        md = "  \n\n  block1  \n\n  block2  \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["block1", "block2"])

    def test_empty_input(self):
        """Test handling of empty input string.
        
        Verifies that:
        - Empty string input returns an empty list
        - No errors are raised on empty input
        """
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_only_whitespace(self):
        """Test handling of whitespace-only input.
        
        Verifies that:
        - Input containing only spaces and newlines returns empty list
        - Various whitespace characters are handled correctly
        """
        md = "   \n\n   \n "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    # New tests for block_to_block_type

    def test_block_to_block_type_heading(self):
        """Test heading detection with edge cases.
        
        Verifies that:
        - All heading levels (h1-h6) are recognized
        - Headings with 0-3 leading spaces are recognized
        - Headings with > 3 leading spaces are treated as paragraphs
        - Closing # marks are optional
        - Space after # is required
        - More than 6 # marks are not valid headings
        """        
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Heading 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Heading 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2 ##"), BlockType.HEADING)
        
        self.assertEqual(block_to_block_type("# "), BlockType.HEADING)
        self.assertEqual(block_to_block_type("   # H1"), BlockType.HEADING)
        self.assertEqual(
            block_to_block_type("    # H1"), BlockType.PARAGRAPH
        )  #Up to 3 leading spaces allowed

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
        """Test code block detection with edge cases.
        
        Verifies that:
        - Code blocks with triple backticks are recognized
        - Language specifiers after backticks are allowed
        - Empty code blocks are valid
        - Whitespace around backticks is permitted
        - Both opening and closing backticks are required
        - Content between backticks can contain any characters
        """
        self.assertEqual(block_to_block_type("```code\nblock\n```"), BlockType.CODE)
        self.assertEqual(
            block_to_block_type("```\nprint('hello')\n```"), BlockType.CODE
        )
        self.assertEqual(block_to_block_type("```  \nsome code\n  ```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("```code block\n\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("```\n```"), BlockType.CODE)  
        self.assertEqual(block_to_block_type("``````"), BlockType.CODE) 
        # Empty code block
        # Changed this test to reflect the actual behavior of the provided regex
        self.assertEqual(
            block_to_block_type("```python\nprint('hi')\n```"), BlockType.CODE
        )  # Language specifier is included in the match
        self.assertEqual(block_to_block_type("code block```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```code block"), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote(self):
        """Test quote block detection with edge cases.
        
        Verifies that:
        - Single-line quotes with > are recognized
        - Multi-line quotes where every line starts with > are recognized
        - Quotes with 0-3 leading spaces before > are valid
        - Quotes with > 3 leading spaces are treated as paragraphs
        - Empty quote lines (just >) are valid
        - All lines must start with > to be a quote block
        """
        # Test the normal cases
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("> Line 1\n> Line 2"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">  indented quote"), BlockType.QUOTE)

        ## These tests are based on the assignment, which expects these to be QUOTE
        
        # Test the valid but unconventional cases(i.e. edge cases)
        self.assertEqual(
            block_to_block_type("> "), BlockType.QUOTE
        )  # Single empty quote line
        self.assertEqual(
            block_to_block_type("> \n> "), BlockType.QUOTE
        )  # Empty quote lines        
        self.assertEqual(
            block_to_block_type("   > Quote"), BlockType.QUOTE
        )  # Up to 3 leading spaces allowed -- added by  

        # Test against the wrong cases
        self.assertEqual(
            block_to_block_type("> Line 1\nLine 2"), BlockType.PARAGRAPH
        )  # Missing '>' on one line
        self.assertEqual(
            block_to_block_type("This is not > a quote"), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("     > Quote"), BlockType.PARAGRAPH
        )  # More than 3 leading spaces not allowed -- added by   

    def test_block_to_block_type_unordered_list(self):
        """Test unordered list detection with edge cases.
        
        Verifies that:
        - Single-line lists with - prefix are recognized
        - Multi-line lists where every line starts with - are recognized
        - Space after - is required
        - Empty list items (just -) are valid
        - All lines must start with - to be an unordered list
        - Inconsistent prefixes across lines break list detection
        """
        # Test the normal cases
        self.assertEqual(
            block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST
        )
        self.assertEqual(
            block_to_block_type("- Another item"), BlockType.UNORDERED_LIST
        )
        self.assertEqual(
            block_to_block_type("-   indented item"), BlockType.UNORDERED_LIST
        )
        ## These tests are based on the assignment, which expects these to be UNORDERED_LIST
        ## The provided block.py code currently classifies "-" and "- \n- " as PARAGRAPH
        
        # Test the valid but unconventional cases(i.e. edge cases)
        self.assertEqual(
            block_to_block_type("- "), BlockType.UNORDERED_LIST
        )  # Single empty list item
        self.assertEqual(
            block_to_block_type("- \n- "), BlockType.UNORDERED_LIST
        )  # Empty list items

        # Test against the wrong cases
        self.assertEqual(
            block_to_block_type("- Item 1\nItem 2"), BlockType.PARAGRAPH
        )  # Missing '-' on one line
        self.assertEqual(block_to_block_type("Not - a list item"), BlockType.PARAGRAPH)
        self.assertEqual(
            block_to_block_type("-Item"), BlockType.PARAGRAPH
        )  # Missing space between '-' and Item

    def test_block_to_block_type_ordered_list(self):
        """Test ordered list detection with edge cases.
        
        Verifies that:
        - Lists with number followed by . and space are recognized
        - Multi-line lists where every line follows pattern are recognized
        - Numbers don't need to be sequential
        - Starting number doesn't need to be 1
        - Numbers can be repeated
        - Space after . is required
        - All lines must match pattern to be an ordered list
        """
        # Test the normal cases
        self.assertEqual(
            block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST
        )
        self.assertEqual(block_to_block_type("1. Item"), BlockType.ORDERED_LIST)
        self.assertEqual(
            block_to_block_type("1. Item 1\n2. Item 2\n3. Item 3"),
            BlockType.ORDERED_LIST,)
        
        # Test the valid but unconventional cases(i.e. edge cases)
        self.assertEqual(
            block_to_block_type("1. Item 1\n3. Item 2"), BlockType.ORDERED_LIST
        )  # Non-sequential numbers but is still valid ordered list
        self.assertEqual(
            block_to_block_type("2. Item 1\n3. Item 2"), BlockType.ORDERED_LIST
        )  # Starting number may not be 1 but still valid ordered list
        self.assertEqual(
            block_to_block_type("1. Item 1\n1. Item 2"), BlockType.ORDERED_LIST
        )  # Repeated number but still valid ordered list

        # Test against the wrong cases
        self.assertEqual(
            block_to_block_type("1. Item 1\n2.Item 2"), BlockType.PARAGRAPH
        )  # Missing space after '.'
        self.assertEqual(
            block_to_block_type("1 Item 1\n2. Item 2"), BlockType.PARAGRAPH
        )  # Missing '.'
        self.assertEqual(
            block_to_block_type("1. Ordered\n- Unordered"), BlockType.PARAGRAPH
        )  # Mixed list types

    def test_block_to_block_type_paragraph(self):
        """Test paragraph detection as fallback type.
        
        Verifies that:
        - Plain text without special formatting is recognized as paragraph
        - Multi-line text without markers is a paragraph
        - Text containing special characters but not matching patterns is paragraph
        - Empty strings default to paragraph type
        - Whitespace-only strings are paragraphs
        - Invalid formatting attempts fall back to paragraph
        """
        # Test the normal cases
        self.assertEqual(
            block_to_block_type("This is a normal paragraph."), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("A paragraph with\nmultiple lines."),
            BlockType.PARAGRAPH,
        )
        self.assertEqual(block_to_block_type("Just some text."), BlockType.PARAGRAPH)

        # Test the valid but unconventional cases(i.e. edge cases)
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
        """Test conversion of markdown paragraphs to HTML.
        
        Verifies that:
        - Multiple paragraphs are wrapped in separate <p> tags
        - Inline formatting within paragraphs is processed
        - Line breaks within blocks don't create new paragraphs
        - All paragraphs are wrapped in a parent <div>
        """
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
        """Test that code blocks preserve content without processing.
        
        Verifies that:
        - Content in code blocks is not processed for inline markdown
        - Markdown syntax characters are preserved literally
        - Code blocks are wrapped in <pre><code> tags
        - Line breaks within code blocks are preserved
        """
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
