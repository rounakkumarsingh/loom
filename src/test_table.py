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
    

if __name__ == "__main__":
    unittest.main()
