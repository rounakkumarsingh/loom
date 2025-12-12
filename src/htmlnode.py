from __future__ import annotations
from typing import Dict, List


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: List[HTMLNode] | None = None,
        props: Dict[str, str] | None = None,
    ) -> None:
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: List[HTMLNode] | None = children
        self.props: Dict[str, str] | None = props

    def to_html(self) -> str:
        raise NotImplementedError("To be implemented soon")

    def props_to_html(self) -> str:
        if not self.props:
            return ""
        final_str = ""
        for prop, value in self.props.items():
            final_str += f' {prop}="{value}"'
        return final_str

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
