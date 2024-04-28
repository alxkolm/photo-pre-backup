from typing import List
import pathlib


def directory_tree():
    pass


def file_list(dirpath: str, recursive=True) -> List[str]:
    """

    :param path:
    :return: List of files in specified directory
    """
    dir = pathlib.Path(dirpath)
    return dir.glob("**/*.*")
