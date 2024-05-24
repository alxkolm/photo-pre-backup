import json
from pathlib import Path
import sqlite3

from commands.thumbnail import get_thumbnail_filepath
from utils.file import list_files, sha256
import config
from utils.exiftool import get_meta
from tqdm import tqdm


def run():
    # command routing
    routing = {
        'remove': run_remove
    }

    if config.options.subcommand not in routing:
        print(f"Unknown sub-command for command `index`: {config.options.subcommand}")
        exit(1)

    routed_function = routing[config.options.subcommand]
    routed_function()


def run_remove():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    db.execute('SELECT original_file_path, file_checksum, thumbnail_file_path FROM backup WHERE is_packed = 1 AND has_thumbnail = 1 AND has_exif = 1')
    # create map with file => checksum
    checksums = {x[0]: {"checksum": x[1], "thumbnail_path": x[2]} for x in db.fetchall()}

    photo_base_path = Path(config.options.photo_dir)
    packed_base_path = Path(config.options.packed_dir)
    thumbnails_base_path = Path(config.options.thumbnails_dir)
    fs = list_files(config.options.photo_dir)
    changed_files = {}
    file_count = 0
    for filepath in tqdm(list(fs)):
        relative_path = str(filepath).replace(config.options.photo_dir, '')
        file_info = checksums.get(relative_path)
        if file_info is None:
            print(f"Skip file {filepath}")
            continue
        # actual_checksum = sha256(filepath)
        # if actual_checksum != file_info['checksum']:
        #     changed_files[relative_path] = {
        #         'actual_checksum': actual_checksum,
        #         'expected_checksum': checksums[relative_path]
        #     }
        #     print(f"Skip file {relative_path}. Checksum does not match.")
        #     continue

        thumbs_file = thumbnails_base_path.joinpath(file_info['thumbnail_path'].strip('/'))
        if not thumbs_file.exists():
            print(f'Thumbnails {file_info["thumbnail_path"]} does not exist for file {relative_path}')
            continue

        print(f"Delete {relative_path}")

        file_count += 1