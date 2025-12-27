from typing import List, Tuple

from textnode import TextType, TextNode
from re import findall


def split_nodes_delimiter(
    old_nodes: List[TextNode], delimiter: str, text_type: TextType
):
    new_nodes: List[TextNode] = []
    for old_node in old_nodes:
        if old_node.node_type != TextType.PLAIN:
            new_nodes.append(old_node)
            continue
        parts = old_node.text.split(delimiter)
        if (len(parts) - 1) & 1:
            # It means no closing delimiter
            raise ValueError(f"Could Not find closing delimiter for {old_node}")
        for idx, part in enumerate(parts):
            if part == "":
                continue
            if not idx & 1:
                new_nodes.append(TextNode(part, TextType.PLAIN))
            else:
                new_nodes.append(TextNode(part, text_type))
    return new_nodes


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    matches = findall(r"!\[([\w\s]+)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    return findall(r"(?<!!)\[([^\]]*)\]\(([^)\s]+(?:\([^)]*\)[^)\s]*)*)\)", text)


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes: List[TextNode] = []
    for node in old_nodes:
        txt = node.text
        this_type = node.node_type
        images = extract_markdown_images(txt)
        if not images:
            new_nodes.append(node)
            continue
        for image in images:
            parts = txt.split(f"![{image[0]}]({image[1]})")
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], this_type))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            txt = parts[1]
        if txt != "":
            new_nodes.append(TextNode(txt, this_type))

    return new_nodes


def split_nodes_link(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes: List[TextNode] = []
    for old_node in old_nodes:
        txt = old_node.text
        this_type = old_node.node_type
        links = extract_markdown_links(txt)
        if not links:
            new_nodes.append(old_node)
            continue
        for link in links:
            parts = txt.split(f"[{link[0]}]({link[1]})")
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], this_type))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            txt = parts[1]
        if txt != "":
            new_nodes.append(TextNode(txt, this_type))

    return new_nodes


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes: List[TextNode] = [TextNode(text, TextType.PLAIN)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    # '_' works for italic only when it is flanked by whitespace
    # or punctuation mark (e.g. this is _italic_ word)
    # But "this is_italic_word does not"
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
