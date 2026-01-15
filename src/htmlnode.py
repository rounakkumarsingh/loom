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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HTMLNode):
            return NotImplemented

        return (
            self.tag == other.tag
            and self.value == other.value
            and self.children == other.children
            and self.props == other.props
        )
    
    def to_html(self) -> str:
        raise NotImplementedError("To be impletemented by subclasses")

    def props_to_html(self) -> str:
        if not self.props:
            return ""
        final_str = ""
        for prop, value in self.props.items():
            final_str += f' {prop}="{value}"'
        return final_str

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
