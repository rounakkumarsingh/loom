import logging
import os
import shutil
from pathlib import Path

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
        elif src / item:
            logger.info(
                f"Copying {(src / item).absolute()} to {(dest / item).absolute()}"
            )
            shutil.copy(src / item, (dest / item))
