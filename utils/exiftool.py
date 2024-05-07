import logging
from typing import Dict

import exiftool

extool = exiftool.ExifToolHelper()


def get_meta(filepath: str) -> Dict:
    try:
        out = extool.get_metadata(filepath)[0]
    except exiftool.exceptions.ExifToolExecuteError as e:
        logging.warning("Couldn't get metadata for file %s", filepath)
        out = {'error': e}
    return out
