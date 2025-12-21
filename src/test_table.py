import unittest
from block import markdown_to_html_node


class TestTableParsing(unittest.TestCase):
    def test_simple_pipe_table(self):
        md = """
| Header A | Header B |
|----------|----------|
| a1       | b1       |
| a2       | b2       |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><table><thead><tr><th>Header A</th><th>Header B</th></tr></thead><tbody><tr><td>a1</td><td>b1</td></tr><tr><td>a2</td><td>b2</td></tr></tbody></table></div>",
        )

    def test_table_with_left_alignment(self):
        """Test table with explicit left alignment (: on left side)"""
        md = """
| Header A | Header B |
|:---------|:---------|
| a1       | b1       |
| a2       | b2       |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        # Left alignment is default, so no align attribute expected
        self.assertEqual(
            html,
            "<div><table><thead><tr><th>Header A</th><th>Header B</th></tr></thead><tbody><tr><td>a1</td><td>b1</td></tr><tr><td>a2</td><td>b2</td></tr></tbody></table></div>",
        )

    def test_table_with_right_alignment(self):
        """Test table with right alignment (: on right side)"""
        md = """
| Header A | Header B |
|---------:|---------:|
| a1       | b1       |
| a2       | b2       |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th align="right">Header A</th><th align="right">Header B</th></tr></thead><tbody><tr><td align="right">a1</td><td align="right">b1</td></tr><tr><td align="right">a2</td><td align="right">b2</td></tr></tbody></table></div>',
        )

    def test_table_with_center_alignment(self):
        """Test table with center alignment (: on both sides)"""
        md = """
| Header A | Header B |
|:--------:|:--------:|
| a1       | b1       |
| a2       | b2       |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th align="center">Header A</th><th align="center">Header B</th></tr></thead><tbody><tr><td align="center">a1</td><td align="center">b1</td></tr><tr><td align="center">a2</td><td align="center">b2</td></tr></tbody></table></div>',
        )

    def test_table_with_mixed_alignment(self):
        """Test table with different alignments per column"""
        md = """
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
| L2   | C2     | R2    |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>Left</th><th align="center">Center</th><th align="right">Right</th></tr></thead><tbody><tr><td>L1</td><td align="center">C1</td><td align="right">R1</td></tr><tr><td>L2</td><td align="center">C2</td><td align="right">R2</td></tr></tbody></table></div>',
        )

    def test_table_with_varying_separator_lengths(self):
        """Test that alignment works with different dash counts"""
        md = """
| A | B | C |
|:---|:-----:|----:|
| a1 | b1    | c1  |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>A</th><th align="center">B</th><th align="right">C</th></tr></thead><tbody><tr><td>a1</td><td align="center">b1</td><td align="right">c1</td></tr></tbody></table></div>',
        )

    def test_table_alignment_with_empty_cells(self):
        """Test that alignment is applied even to empty cells"""
        md = """
| Header A | Header B |
|:--------:|---------:|
|          | value    |
| value2   |          |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th align="center">Header A</th><th align="right">Header B</th></tr></thead><tbody><tr><td align="center"></td><td align="right">value</td></tr><tr><td align="center">value2</td><td align="right"></td></tr></tbody></table></div>',
        )

    def test_header_only_table(self):
        """Test table with header and separator but no data rows"""
        md = """
| Header A | Header B | Header C |
|----------|:--------:|---------:|
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>Header A</th><th align="center">Header B</th><th align="right">Header C</th></tr></thead></table></div>',
        )

    def test_header_only_table_with_whitespace(self):
        """Test header-only table with trailing whitespace lines"""
        md = """
| Col1 | Col2 |
|------|------|

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>Col1</th><th>Col2</th></tr></thead></table></div>',
        )

    def test_table_with_fewer_body_cells(self):
        """Test table where body rows have fewer cells than header (should be padded)"""
        md = """
| Header A | Header B | Header C |
|----------|----------|----------|
| a1       | b1       |
| a2       |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>Header A</th><th>Header B</th><th>Header C</th></tr></thead><tbody><tr><td>a1</td><td>b1</td><td></td></tr><tr><td>a2</td><td></td><td></td></tr></tbody></table></div>',
        )

    def test_table_with_more_body_cells(self):
        """Test table where body rows have more cells than header"""
        md = """
| Header A | Header B |
|----------|----------|
| a1       | b1       | c1       | d1       |
| a2       | b2       | c2       |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>Header A</th><th>Header B</th></tr></thead><tbody><tr><td>a1</td><td>b1</td><td>c1</td><td>d1</td></tr><tr><td>a2</td><td>b2</td><td>c2</td></tr></tbody></table></div>',
        )

    def test_table_mismatched_cells_with_alignment(self):
        """Test that alignment is preserved even with mismatched cell counts"""
        md = """
| Left | Center | Right |
|:-----|:------:|------:|
| L1   |
| L2   | C2     | R2    | Extra |
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><table><thead><tr><th>Left</th><th align="center">Center</th><th align="right">Right</th></tr></thead><tbody><tr><td>L1</td><td align="center"></td><td align="right"></td></tr><tr><td>L2</td><td align="center">C2</td><td align="right">R2</td><td>Extra</td></tr></tbody></table></div>',
        )


if __name__ == "__main__":
    unittest.main()