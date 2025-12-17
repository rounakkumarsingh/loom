import logging
import os
from pathlib import Path
import re
import shutil
from block import markdown_to_html_node


def extract_title(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if not match:
        raise ValueError("No H1 title found")
    return match.group(1).strip()


logger = logging.getLogger(__name__)


def copy_recursive(src: Path, dest: Path):
    logger.info(f"copying {src.absolute()}")
    if dest.exists() and dest.is_dir():
        shutil.rmtree(dest)
    os.mkdir(dest)
    logger.info(f"Creating dir {dest.absolute()}")
    for item in os.listdir(src):
        if (src / item).is_dir():
            copy_recursive(src / item, dest / item)
        else:
            logger.info(
                f"Copying {(src / item).absolute()} to {(dest / item).absolute()}"
            )
            shutil.copy(src / item, (dest / item))


def generate_page(from_path: Path, template_path: Path, dest_path: Path):
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


def generate_page_recursively(
    dir_path_content: Path, template_path: Path, dest_dir_path: Path
):
    dest_dir_path.mkdir(exist_ok=True)

    for entry in dir_path_content.iterdir():
        if entry.is_dir():
            generate_page_recursively(
                entry,
                template_path,
                dest_dir_path / entry.name,
            )
        elif entry.suffix == ".md":
            generate_page(
                entry,
                template_path,
                dest_dir_path / (entry.stem + ".html"),
            )


def main():
    logging.basicConfig(level=logging.INFO)

    public = Path("public")
    if public.exists():
        shutil.rmtree(public)
    public.mkdir()

    copy_recursive(Path("static"), public)
    generate_page_recursively(Path("content"), Path("template.html"), public)


if __name__ == "__main__":
    main()
