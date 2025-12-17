import logging
from pathlib import Path
from website_utils import copy_recursive


def main():
    logging.basicConfig(level=logging.INFO)
    copy_recursive(Path("./static"), Path("./public"))


if __name__ == "__main__":
    main()
