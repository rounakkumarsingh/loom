from enum import Enum
from typing import List, Optional

from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode

class TextType(Enum):
    PLAIN = "PLAIN"
    BOLD = "BOLD"
    ITALIC = "ITALIC"
    CODE = "CODE"
    LINK = "LINK"
    IMAGE = "IMAGE"


class TextNode:
    def __init__(self, txt: str, node_type: TextType, url: str | None = None, children: Optional[List["TextNode"]] = None,) -> None:
        self.text: str = txt
        self.node_type: TextType = node_type
        self.url: str | None = url
        self.children: List[TextNode] = children if children is not None else []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextNode):
            return NotImplemented

        return (
            self.text == other.text
            and self.node_type == other.node_type
            and self.url == other.url
            and self.children == other.children
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.node_type.value}, {self.url})" 

# Mapping for inline container nodes
INLINE_TAG_MAP = {
    TextType.BOLD: "b",
    TextType.ITALIC: "i",
    TextType.CODE: "code",
}


def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    # for parent (nested)
    if text_node.children:
        tag = INLINE_TAG_MAP.get(text_node.node_type)
        if tag is None:
            raise ValueError(f"TextType {text_node.node_type} cannot have children")
        return ParentNode(
            tag=tag,
            children=[text_node_to_html_node(child) for child in text_node.children],
        )

    if text_node.node_type == TextType.PLAIN:
        return LeafNode(tag=None, value=text_node.text)
    elif text_node.node_type == TextType.BOLD:
        return LeafNode("b", value=text_node.text)
    elif text_node.node_type == TextType.ITALIC:
        return LeafNode("i", value=text_node.text)
    elif text_node.node_type == TextType.CODE:
        return LeafNode("code", value=text_node.text)
    elif text_node.node_type == TextType.LINK:
        return LeafNode(
            "a",
            text_node.text,
            {"href": text_node.url if text_node.url is not None else ""},
        )
    elif text_node.node_type == TextType.IMAGE:
        return LeafNode(
            "img",
            "",
            {
                "src": text_node.url if text_node.url is not None else "",
                "alt": text_node.text,
            },
        )
    else:
        raise ValueError("Missed this testcase, please fix", text_node.__repr__())
