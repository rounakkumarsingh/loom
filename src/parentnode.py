from typing import Dict, List
from htmlnode import HTMLNode


class ParentNode(HTMLNode):
    def __init__(
        self, tag: str, children: List[HTMLNode], props: Dict[str, str] | None = None
    ) -> None:
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("None tag for parent node")
        if not self.children:
            raise ValueError("None children tag for parent node")
        props_html = self.props_to_html()
        children_html = "".join([child.to_html() for child in self.children])
        return f"<{self.tag}{props_html}>{children_html}</{self.tag}>"
