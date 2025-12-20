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


if __name__ == "__main__":
    unittest.main()
