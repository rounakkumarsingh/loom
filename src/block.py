from enum import Enum
from re import fullmatch, search
from typing import List

from htmlnode import HTMLNode
from inline import text_to_textnodes
from leafnode import LeafNode
from parentnode import ParentNode
from textnode import TextNode, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "PARAGRAPH"
    HEADING = "HEADING"
    CODE = "CODE"
    QUOTE = "QUOTE"
    UNORDERED_LIST = "UNORDERED_LIST"
    ORDERED_LIST = "ORDERED_LIST"


def markdown_to_blocks(markdown: str) -> List[str]:
    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks if block.strip()]
    return blocks


def is_ordered_list(block: str) -> bool:
    block = block.strip()
    if not block:
        return False
    expected = 1
    for line in block.splitlines():
        m = fullmatch(r"(\d+)\.\s.+", line)
        if not m:
            return False
        num = int(m.group(1))
        if num != expected:
            return False
        expected += 1
    return True


def block_to_block_type(markdown) -> BlockType:
    if markdown == "":
        return BlockType.PARAGRAPH
    if search(r"^#{1,6}\s+(.*)$", markdown):
        return BlockType.HEADING
    elif search(r"`{3}([\s\S]*?)`{3}", markdown):
        return BlockType.CODE
    elif all(fullmatch(r"\s{0,3}>\s?(.*)", line) for line in markdown.splitlines()):
        return BlockType.QUOTE
    elif all(fullmatch(r"-\s*(.+)", line) for line in markdown.splitlines()):
        return BlockType.UNORDERED_LIST
    elif is_ordered_list(markdown):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH


def html_node_regex_match(
    pattern: str, text: str, subparent: str | None = None
) -> List[HTMLNode]:
    text_nodes: List[TextNode] = []
    html_nodes: List[HTMLNode] = []
    for line in text.splitlines():
        m = fullmatch(pattern, line)
        assert m is not None
        inline_txt = m.group(1)
        if subparent is not None:
            subparent_node = ParentNode(
                subparent,
                [
                    text_node_to_html_node(text_node)
                    for text_node in text_to_textnodes(inline_txt)
                ],
            )
            html_nodes.append(subparent_node)
        else:
            text_nodes.extend(text_to_textnodes(inline_txt))
    if subparent is not None:
        return html_nodes
    return [text_node_to_html_node(node) for node in text_nodes]


def text_to_children(text: str) -> List[HTMLNode]:
    block_type = block_to_block_type(text)
    match block_type:
        case BlockType.HEADING:
            return html_node_regex_match(r"^#{1,6}\s+(.+)$", text)
        case BlockType.PARAGRAPH:
            text = text.replace("\n", " ")
            return [text_node_to_html_node(node) for node in text_to_textnodes(text)]
        case BlockType.QUOTE:
            return html_node_regex_match(r"\s{0,3}>\s?(.*)", text)
        case BlockType.UNORDERED_LIST:
            return html_node_regex_match(r"-\s*(.+)", text, "ul")
        case BlockType.ORDERED_LIST:
            return html_node_regex_match(r"\d+\.\s*(\S.+)", text, "ol")
        case BlockType.CODE:
            raise AssertionError("How the hell control reach here")


def get_block_html_node(markdown_block: str) -> HTMLNode:
    block_type = block_to_block_type(markdown_block)
    match block_type:
        case BlockType.PARAGRAPH:
            return ParentNode("p", text_to_children(markdown_block))
        case BlockType.HEADING:
            m = fullmatch(r"^(#{1,6})\s+.*$", markdown_block)
            assert m is not None

            hashes = m.group(1)
            return ParentNode(f"h{len(hashes)}", text_to_children(markdown_block))
        case BlockType.CODE:
            m = fullmatch(r"`{3}[^\n]*\n([\s\S]*?)`{3}", markdown_block)
            assert m is not None
            code_snippet = m.group(1)
            return ParentNode("pre", [LeafNode("code", code_snippet)])
        case BlockType.QUOTE:
            return ParentNode("blockquote", text_to_children(markdown_block))
        case BlockType.UNORDERED_LIST:
            return ParentNode("ul", text_to_children(markdown_block))
        case BlockType.ORDERED_LIST:
            return ParentNode("ol", text_to_children(markdown_block))


def markdown_to_html_node(markdown: str) -> HTMLNode:
    blocks = markdown_to_blocks(markdown)
    root_element = ParentNode("div", [])
    for block in blocks:
        html_node = get_block_html_node(block)
        if root_element.children is None:
            raise ValueError("WTF is happening")
        root_element.children.append(html_node)
    return root_element
