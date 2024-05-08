import hashlib
import pathlib
from typing import List


def directory_tree():
    pass


def list_files(dirpath: str, recursive=True) -> List[str]:
    """

    :param path:
    :return: List of files in specified directory
    """
    dir = pathlib.Path(dirpath)
    return dir.glob("**/*.*")


def sha256(fname):
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
