from typing import List


def markdown_to_blocks(markdown: str) -> List[str]:
    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks if block.strip()]
    return blocks
