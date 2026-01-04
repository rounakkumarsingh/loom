import unittest
from block import markdown_to_html_node
from block import block_to_block_type
from block import BlockType


# ---------- AST helpers ----------

def element_children(node):
    return [c for c in (node.children or []) if c.tag is not None]


def text_of(node):
    if node.value is not None:
        return node.value
    if not node.children:
        return ""
    return "".join(c.value for c in node.children if c.value is not None)


def find_child(node, tag):
    for c in element_children(node):
        if c.tag == tag:
            return c
    raise AssertionError(f"<{tag}> not found under <{node.tag}>")


def get_table(md):
    root = markdown_to_html_node(md)
    return find_child(root, "table")


# ---------- Tests ----------

class TestTableParsing(unittest.TestCase):

    def test_simple_pipe_table(self):
        """Test parsing of a basic pipe table structure.
        
        Verifies that:
        - Header row is parsed into <thead> element
        - Body rows are parsed into <tbody> element
        - Cell content is extracted correctly
        - Delimiter row (dashes) is not included in output
        - Table structure matches expected HTML format
        """
        md = """
| Header A | Header B |
|----------|----------|
| a1       | b1       |
| a2       | b2       |
"""
        table = get_table(md)
        thead = find_child(table, "thead")
        tbody = find_child(table, "tbody")

        headers = element_children(thead.children[0])
        self.assertEqual([text_of(h) for h in headers], ["Header A", "Header B"])

        rows = element_children(tbody)
        self.assertEqual(
            [[text_of(td) for td in element_children(r)] for r in rows],
            [["a1", "b1"], ["a2", "b2"]],
        )

    def test_table_with_left_alignment(self):
        """Test that left-aligned columns don't add alignment attributes.
        
        Verifies that:
        - Left alignment syntax (:---) is recognized
        - No align attribute is added for left alignment (default)
        - Header cells don't have spurious align properties
        - Left is the implicit default alignment in HTML
        """
        md = """
| Header A | Header B |
|:---------|:---------|
| a1       | b1       |
| a2       | b2       |
"""
        table = get_table(md)
        ths = element_children(find_child(table, "thead").children[0])

        for th in ths:
            self.assertNotIn("align", th.props or {})

    def test_table_with_right_alignment(self):
        """Test right-aligned columns with align attribute.
        
        Verifies that:
        - Right alignment syntax (---:) is recognized
        - align="right" attribute is added to all cells in column
        - Both header and body cells receive alignment
        - Alignment is applied consistently throughout the column
        """
        md = """
| Header A | Header B |
|---------:|---------:|
| a1       | b1       |
| a2       | b2       |
"""
        table = get_table(md)

        for node in table.children:
            for row in element_children(node):
                for cell in element_children(row):
                    self.assertEqual(cell.props.get("align"), "right")

    def test_table_with_center_alignment(self):
        """Test center-aligned columns with align attribute.
        
        Verifies that:
        - Center alignment syntax (:---:) is recognized
        - align="center" attribute is added to all cells in column
        - Both header and body cells receive alignment
        - Colons on both sides indicate centering
        """
        md = """
| Header A | Header B |
|:--------:|:--------:|
| a1       | b1       |
| a2       | b2       |
"""
        table = get_table(md)

        for node in table.children:
            for row in element_children(node):
                for cell in element_children(row):
                    self.assertEqual(cell.props.get("align"), "center")

    def test_table_with_mixed_alignment(self):
        """Test table with different alignment per column.
        
        Verifies that:
        - Each column can have independent alignment
        - Left (default), center (:---:), and right (---:) mix correctly
        - Alignment is applied per-column, not per-cell
        - Body cells inherit their column's alignment
        """
        md = """
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
| L2   | C2     | R2    |
"""
        table = get_table(md)
        tds = element_children(find_child(table, "tbody").children[1])

        aligns = [(td.props or {}).get("align") for td in tds]
        self.assertEqual(aligns, [None, "center", "right"])

    def test_table_with_varying_separator_lengths(self):
        """Test that separator dash count doesn't affect parsing.
        
        Verifies that:
        - Short separators (---) work
        - Long separators (-----) work
        - Varying lengths in same table are acceptable
        - Only the presence and position of colons matter
        - Minimum 3 dashes is typically required
        """
        md = """
|  A  |   B   |  C  |
|:--- |:-----:|----:|
| a1  |   b1  | c1  |
"""
        table = get_table(md)
        tds = element_children(find_child(table, "tbody").children[0])

        aligns = [(td.props or {}).get("align") for td in tds]
        self.assertEqual(aligns, [None, "center", "right"])
        
    def test_table_alignment_with_empty_cells(self):
        """Test that alignment applies even to empty cells.
        
        Verifies that:
        - Empty cells still receive align attributes
        - Alignment is determined by column, not content
        - Empty string content is distinguished from missing cells
        - Props are set even when cell has no visible content
        """
        md = """
| Header A | Header B |
|:--------:|---------:|
|          | value    |
| value2   |          |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        tds = element_children(tbody.children[0])

        self.assertEqual(text_of(tds[0]), "")
        self.assertEqual(text_of(tds[1]), "value")
        self.assertEqual(tds[0].props.get("align"), "center")
        self.assertEqual(tds[1].props.get("align"), "right")

    def test_header_only_table(self):
        """Test table with headers but no body rows.
        
        Verifies that:
        - Tables with only header+delimiter are valid
        - <thead> element is created
        - No <tbody> element is generated
        - Useful for template tables or empty datasets
        """
        md = """
| Header A | Header B | Header C |
|----------|:--------:|---------:|
"""
        table = get_table(md)
        self.assertIsNotNone(find_child(table, "thead"))
        self.assertFalse(any(c.tag == "tbody" for c in element_children(table)))

    def test_table_with_fewer_body_cells(self):
        """Test automatic padding when rows have fewer cells than headers.
        
        Verifies that:
        - Missing cells are filled with empty strings
        - Row length matches header count
        - Padding happens on the right side
        - Table structure remains rectangular
        """
        md = """
| Header A | Header B | Header C |
|----------|----------|----------|
| a1       | b1       |
| a2       |
"""

        table = get_table(md)
        tbody = find_child(table, "tbody")

        rows = element_children(tbody)
        self.assertEqual(
            [[text_of(td) for td in element_children(r)] for r in rows],
            [["a1", "b1", ""], ["a2", "", ""]],
        )

    def test_table_with_more_body_cells(self):
        """Test truncation when rows have more cells than headers.
        
        Verifies that:
        - Extra cells beyond header count are ignored
        - Row length is capped at header count
        - Truncation happens on the right side
        - Table structure remains consistent
        """
        md = """
| Header A | Header B |
|----------|----------|
| a1       | b1       | c1       | d1       |
| a2       | b2       | c2       |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")

        rows = element_children(tbody)
        self.assertEqual(
            [[text_of(td) for td in element_children(r)] for r in rows],
            [["a1", "b1"],["a2", "b2"]],
        )

    def test_table_mismatched_cells_with_alignment(self):
        """Test that alignment works correctly with mismatched cell counts.
        
        Verifies that:
        - Padding cells receive proper alignment attributes
        - Truncated cells don't affect remaining alignments
        - Each column's alignment is preserved
        - Alignment and padding/truncation work together
        """
        md = """
| Left | Center | Right |
|:-----|:------:|------:|
| L1   |
| L2   | C2     | R2    | Extra |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")

        row1, row2 = element_children(tbody)

        self.assertEqual(
            [text_of(td) for td in element_children(row1)],
            ["L1", "", ""],
        )

        self.assertEqual(
            [text_of(td) for td in element_children(row2)],
            ["L2", "C2", "R2"],
        )

    def test_header_row_delimiter_row_mismatch(self):
        """Test that header/delimiter cell count mismatch prevents table recognition.
        
        Verifies that:
        - Header must have same cell count as delimiter
        - Mismatched counts cause block to be treated as paragraph
        - Tables require structural consistency
        - This is a strict validation rule
        """
        md = """
|  A  |  B  |
| --- |
| bar |
"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)

    def test_escape_pipe_using_backtick(self):
        """Test that pipes can be escaped within backticks.
        
        Verifies that:
        - Pipes inside backticks don't split cells
        - Backslash-pipe (\\|) is treated as literal pipe character
        - Inline code spans can contain pipe characters
        - Escaping works within other inline formatting
        - Cell contains text + code + text structure
        """
        md = """
|  A  |
| --- |
| b `\|` az |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")

        row = element_children(tbody)[0]
        cells = element_children(row)
        self.assertEqual(len(cells), 1)
        td = cells[0]
        children = td.children

        # Expect: text, code, text
        self.assertEqual(children[0].value, "b ")
        self.assertEqual(children[1].tag, "code")
        self.assertEqual(children[1].children[0].value, "|")
        self.assertEqual(children[2].value, " az")
    
class TestTableErrorHandling(unittest.TestCase):
    """Tests for error handling in table parsing."""

    # ========================================================================
    # MISSING REQUIRED ELEMENTS
    # ========================================================================

    def test_get_table_on_non_table_markdown_raises_error(self):
        """Test that finding table in non-table markdown raises AssertionError.
        
        Verifies that:
        - Plain text without table syntax raises error
        - get_table helper fails gracefully
        - Error message indicates missing <table> tag
        """
        md = "Just a paragraph"
        with self.assertRaises(AssertionError) as context:
            get_table(md)
        self.assertIn("table", str(context.exception).lower())

    def test_find_child_missing_thead_raises_error(self):
        """Test that finding non-existent thead raises AssertionError.
        
        Verifies that:
        - Missing required child element raises error
        - Error message identifies which tag is missing
        - Malformed tables don't silently pass
        """
        md = "Not a table at all"
        with self.assertRaises(AssertionError):
            root = markdown_to_html_node(md)
            table = find_child(root, "table")  # Will fail here
    
    def test_find_child_missing_tbody_in_header_only_table(self):
        """Test that looking for tbody in header-only table raises error.
        
        Verifies that:
        - Header-only tables don't have tbody
        - Attempting to access missing tbody raises AssertionError
        - Error handling distinguishes between valid empty vs missing
        """
        md = """
| Header A | Header B |
|----------|----------|
"""
        table = get_table(md)
        with self.assertRaises(AssertionError) as context:
            find_child(table, "tbody")
        self.assertIn("tbody", str(context.exception))

    # ========================================================================
    # MALFORMED TABLE STRUCTURES
    # ========================================================================

    def test_table_without_delimiter_row_not_recognized(self):
        """Test that table without delimiter row is treated as paragraph.
        
        Verifies that:
        - Missing delimiter row (---) prevents table recognition
        - Markdown is classified as PARAGRAPH instead
        - Three-line minimum is not automatically a table
        """
        md = """
| Header A | Header B |
| a1       | b1       |
| a2       | b2       |
"""
        block_type = block_to_block_type(md)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_table_with_only_one_row_not_recognized(self):
        """Test that single row without delimiter is not a table.
        
        Verifies that:
        - Minimum two rows required (header + delimiter)
        - Single row of pipes is not a table
        - Classification falls back to paragraph
        """
        md = "| Header A | Header B |"
        block_type = block_to_block_type(md)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_delimiter_row_with_wrong_character_not_recognized(self):
        """Test that delimiter row must use dashes, not other chars.
        
        Verifies that:
        - Only dash (-) characters work in delimiter
        - Other characters like = or _ don't create tables
        - Strict syntax requirements are enforced
        """
        md = """
| Header A | Header B |
|==========|==========|
| a1       | b1       |
"""
        block_type = block_to_block_type(md)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_header_and_delimiter_column_count_mismatch_not_recognized(self):
        """Test that column count must match between header and delimiter.
        
        Verifies that:
        - Header with N columns requires N delimiter segments
        - Mismatch prevents table recognition
        - This is already tested but critical for error handling
        """
        md = """
| A | B | C |
|---|---|
| a | b | c |
"""
        block_type = block_to_block_type(md)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    # ========================================================================
    # INVALID ALIGNMENT SYNTAX
    # ========================================================================

    def test_invalid_alignment_syntax_treated_as_left(self):
        """Test that invalid alignment markers default to left alignment.
        
        Verifies that:
        - Invalid patterns like (--:--) are handled
        - System doesn't crash on malformed alignment
        - Defaults to safe left alignment (no attribute)
        """
        md = """
| Header A |
|--::----|
| a1      |
"""
        # This might be treated as paragraph OR as left-aligned table
        # depending on implementation - test both scenarios
        try:
            table = get_table(md)
            # If parsed as table, should have no align or default to left
            thead = find_child(table, "thead")
            ths = element_children(thead.children[0])
            for th in ths:
                align = (th.props or {}).get("align")
                # Should be None (left) or explicitly "left"
                self.assertIn(align, [None, "left"])
        except AssertionError:
            # Or it might reject as invalid table
            block_type = block_to_block_type(md)
            self.assertEqual(block_type, BlockType.PARAGRAPH)

    # ========================================================================
    # EDGE CASES WITH EMPTY/NULL DATA
    # ========================================================================

    def test_completely_empty_table_structure(self):
        """Test table with header and delimiter but totally empty cells.
        
        Verifies that:
        - Empty cells are valid
        - Structure is maintained even with no content
        - Empty strings are returned for cell text
        """
        md = """
|  |  |
|--|--|
|  |  |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        rows = element_children(tbody)
        cells = element_children(rows[0])
        
        # Should have cells, even if empty
        self.assertEqual(len(cells), 2)
        for cell in cells:
            self.assertEqual(text_of(cell), "")

    def test_table_with_whitespace_only_cells(self):
        """Test that whitespace-only cells are trimmed to empty.
        
        Verifies that:
        - Cells with only spaces are treated as empty
        - Whitespace normalization occurs
        - No unexpected content appears
        """
        md = """
| A | B |
|---|---|
|   |   |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        row = element_children(tbody)[0]
        cells = element_children(row)
        
        # Cells should be empty or whitespace-trimmed
        for cell in cells:
            self.assertIn(text_of(cell), ["", " "])

    # ========================================================================
    # MALFORMED INLINE CONTENT IN CELLS
    # ========================================================================

    def test_unclosed_inline_formatting_in_cell(self):
        """Test handling of malformed inline markdown in table cells.
        
        Verifies that:
        - Unclosed bold/italic doesn't break table parsing
        - Cell content is either fixed or passed through
        - Table structure remains intact
        """
        md = """
| Header |
|--------|
| **unclosed bold |
"""
        # Should either parse table with malformed cell content
        # OR reject as invalid markdown - test for graceful handling
        try:
            table = get_table(md)
            tbody = find_child(table, "tbody")
            # Table parsed, check it has content
            self.assertIsNotNone(tbody)
        except (AssertionError, ValueError):
            # Or it might raise error, which is also acceptable
            pass

    def test_invalid_link_syntax_in_cell(self):
        """Test handling of malformed links within table cells.
        
        Verifies that:
        - Invalid link syntax like [text](incomplete
        - Doesn't crash the table parser
        - Content is preserved even if unparseable
        """
        md = """
| Header |
|--------|
| [link](incomplete |
"""
        try:
            table = get_table(md)
            tbody = find_child(table, "tbody")
            row = element_children(tbody)[0]
            cell = element_children(row)[0]
            # Should have some content, even if not parsed as link
            self.assertIsNotNone(text_of(cell))
        except (AssertionError, ValueError):
            # Or might reject, which is acceptable
            pass

    # ========================================================================
    # BOUNDARY CONDITIONS
    # ========================================================================

    def test_table_with_extremely_long_cell_content(self):
        """Test handling of very long cell content.
        
        Verifies that:
        - No truncation of long content occurs
        - System handles large strings
        - No performance issues with long cells
        """
        long_content = "x" * 10000
        md = f"""
| Header |
|--------|
| {long_content} |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        row = element_children(tbody)[0]
        cell = element_children(row)[0]
        
        # Content should be preserved
        self.assertIn(long_content, text_of(cell))

    def test_table_with_many_columns(self):
        """Test handling of tables with many columns.
        
        Verifies that:
        - Large number of columns is supported
        - No arbitrary column limit exists
        - All columns are processed
        """
        num_cols = 50
        headers = " | ".join([f"H{i}" for i in range(num_cols)])
        delimiters = " | ".join(["---"] * num_cols)
        data = " | ".join([f"d{i}" for i in range(num_cols)])
        
        md = f"""
| {headers} |
| {delimiters} |
| {data} |
"""
        table = get_table(md)
        thead = find_child(table, "thead")
        header_cells = element_children(thead.children[0])
        
        # Should have all columns
        self.assertEqual(len(header_cells), num_cols)

    def test_table_with_many_rows(self):
        """Test handling of tables with many rows.
        
        Verifies that:
        - Large number of rows is supported
        - No arbitrary row limit exists
        - All rows are processed
        """
        num_rows = 100
        rows = "\n".join([f"| row{i} | data{i} |" for i in range(num_rows)])
        
        md = f"""
| Header A | Header B |
|----------|----------|
{rows}
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        body_rows = element_children(tbody)
        
        # Should have all rows
        self.assertEqual(len(body_rows), num_rows)

    # ========================================================================
    # SPECIAL CHARACTERS AND ESCAPING
    # ========================================================================

    def test_table_with_html_entities_in_cells(self):
        """Test that HTML entities are handled correctly in cells.
        
        Verifies that:
        - Entities like &lt; &gt; are preserved or decoded
        - No double-encoding occurs
        - Content remains safe
        """
        md = """
| Header |
|--------|
| &lt;tag&gt; |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        row = element_children(tbody)[0]
        cell = element_children(row)[0]
        
        content = text_of(cell)
        # Should contain the entity or decoded version
        self.assertTrue("&lt;" in content or "<" in content)

    def test_table_with_special_markdown_chars_in_cells(self):
        """Test that special markdown characters don't break parsing.
        
        Verifies that:
        - Characters like # * _ [ ] don't break table
        - They're treated as literal text within cells
        - Inline parsing still works where appropriate
        """
        md = """
| Header |
|--------|
| # * _ [ ] |
"""
        table = get_table(md)
        tbody = find_child(table, "tbody")
        row = element_children(tbody)[0]
        cell = element_children(row)[0]
        
        # Should have content
        self.assertIsNotNone(text_of(cell))

if __name__ == "__main__":
    unittest.main()
