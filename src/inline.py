from typing import List, Tuple, Optional, Dict

from textnode import TextType, TextNode
from re import findall

INLINE_DELIMITERS: Dict[str, TextType] = {
    "**": TextType.BOLD,
    "_": TextType.ITALIC,
    "`": TextType.CODE,
}


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


def collapse_single_child_nodes(nodes: List[TextNode]) -> None:
    for i, node in enumerate(nodes):
        if not node.children:
            continue

        if len(node.children) == 1:
            only_child = node.children[0]
            if node.text == "":
                nodes[i] = TextNode(
                    only_child.text,
                    node.node_type,
                )
        else:
            collapse_single_child_nodes(node.children)


def match_delimiter_at(
    index: int,
    text: str,
) -> Optional[str]:
    for delimiter in INLINE_DELIMITERS:
        if text.startswith(delimiter, index):
            return delimiter
    return None


def parse_inline_with_stack(
    nodes: List[TextNode],
) -> List[TextNode]:
    parsed_nodes: List[TextNode] = []

    for node in nodes:
        if node.node_type != TextType.PLAIN:
            parsed_nodes.append(node)
            continue

        text = node.text
        open_stack: List[Tuple[str, TextNode]] = []

        root = TextNode("", TextType.PLAIN)
        root.children = []

        current_parent = root
        buffer = ""
        index = 0

        while index < len(text):
            delimiter = match_delimiter_at(index, text)

            if delimiter:
                if open_stack and open_stack[-1][0] == delimiter:
                    # closing delimiter
                    if buffer:
                        current_parent.children.append(TextNode(buffer, TextType.PLAIN))
                    buffer = ""

                    _, previous_parent = open_stack.pop()
                    current_parent = previous_parent
                else:
                    # opening delimiter
                    if buffer:
                        current_parent.children.append(TextNode(buffer, TextType.PLAIN))
                    buffer = ""

                    open_stack.append((delimiter, current_parent))

                    new_node = TextNode("", INLINE_DELIMITERS[delimiter])
                    new_node.children = []
                    current_parent.children.append(new_node)
                    current_parent = new_node

                index += len(delimiter)
                continue

            buffer += text[index]
            index += 1

        if open_stack:
            raise ValueError(
                f"Could not find closing delimiter for {open_stack[-1][0]}"
            )

        if buffer:
            current_parent.children.append(TextNode(buffer, TextType.PLAIN))

        parsed_nodes.extend(root.children)

    return parsed_nodes

    # print(ParentNode("div", [text_node_to_html_node(node) for node in newnodes]).to_html())
    return newnodes


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    matches = findall(r"!\[([\w\s]+)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    return findall(r"(?<!!)\[([^\]]*)\]\(([^)\s]+(?:\([^)]*\)[^)\s]*)*)\)", text)


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes: List[TextNode] = []
    for node in old_nodes:
        if node.children:
            node.children = split_nodes_image(node.children)
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
        if old_node.children:
            old_node.children = split_nodes_link(old_node.children)
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

    nodes = parse_inline_with_stack(nodes)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    collapse_single_child_nodes(nodes)

    return nodes
