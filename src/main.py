import logging
from pathlib import Path
import re
from website_utils import copy_recursive
from block import markdown_to_html_node


def extract_title(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if not match:
        raise ValueError("No H1 title found")
    return match.group(1).strip()


def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = Path(from_path).read_text()
    template = Path(template_path).read_text()
    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    dest = Path(dest_path)
    with open(dest, "w") as f:
        f.write(template)


def main():
    logging.basicConfig(level=logging.INFO)
    copy_recursive(Path("static"), Path("public"))
    generate_page("content/index.md", "template.html", "public/index.html")


if __name__ == "__main__":
    main()
