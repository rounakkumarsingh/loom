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
        md = """
| Header A | Header B | Header C |
|----------|:--------:|---------:|
"""
        table = get_table(md)
        self.assertIsNotNone(find_child(table, "thead"))
        self.assertFalse(any(c.tag == "tbody" for c in element_children(table)))

    def test_table_with_fewer_body_cells(self):
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
        """The header row must match the delimiter row in the number of cells. If not, a table will not be recognized"""
        md = """
|  A  |  B  |
| --- |
| bar |
"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)

    def test_escape_pipe_using_backtick(self):
        """Include a pipe in a cell's content by escaping it, including inside other inline spans"""
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
