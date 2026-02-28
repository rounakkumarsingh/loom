import logging
import sys
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

    dest.mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating dir {dest.absolute()}")

    for item in src.iterdir():
        if item.is_dir():
            copy_recursive(item, dest / item.name)
        else:
            logger.info(f"Copying {item.absolute()} to {(dest / item.name).absolute()}")
            shutil.copy(item, dest / item.name)


def generate_page(
    from_path: Path,
    template_path: Path,
    dest_path: Path,
    basepath: str,
):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    markdown = from_path.read_text()
    template = template_path.read_text()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)

    # Apply basepath to absolute links
    template = template.replace('href="/', f'href="{basepath}')
    template = template.replace('src="/', f'src="{basepath}')

    dest_path.write_text(template)


def generate_page_recursively(
    dir_path_content: Path,
    template_path: Path,
    dest_dir_path: Path,
    basepath: str,
):
    dest_dir_path.mkdir(parents=True, exist_ok=True)

    for entry in dir_path_content.iterdir():
        if entry.is_dir():
            generate_page_recursively(
                entry,
                template_path,
                dest_dir_path / entry.name,
                basepath,
            )
        elif entry.suffix == ".md":
            generate_page(
                entry,
                template_path,
                dest_dir_path / (entry.stem + ".html"),
                basepath,
            )


def main():
    logging.basicConfig(level=logging.INFO)

    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    if not basepath.endswith("/"):
        basepath += "/"

    public = Path("docs")
    if public.exists():
        shutil.rmtree(public)
    public.mkdir()

    copy_recursive(Path("static"), public)

    generate_page_recursively(
        Path("content"),
        Path("template.html"),
        public,
        basepath,
    )


if __name__ == "__main__":
    main()
