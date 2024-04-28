from typing import List
import pathlib


def directory_tree():
    pass


def list_files(dirpath: str, recursive=True) -> List[str]:
    """

    :param path:
    :return: List of files in specified directory
    """
    dir = pathlib.Path(dirpath)
    return dir.glob("**/*.*")
