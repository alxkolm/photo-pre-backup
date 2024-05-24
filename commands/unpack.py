import datetime
import logging
import sqlite3
import tarfile
from pathlib import Path
from tqdm import tqdm
from uuid_extensions import uuid7

import config


def run():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    params = config.options
    photo_base_path = Path(config.options.photo_dir)
    packed_base_path = Path(config.options.packed_dir)
    unpack_base_path = photo_base_path.parent.joinpath("unpacked_test")
    unpack_base_path.mkdir(parents=True, exist_ok=True)

    db.execute('SELECT packed_file_path,original_file_path FROM backup WHERE is_packed = 1 AND original_file_path GLOB :path_pattern ORDER BY original_file_path',
               {'path_pattern': config.options.path})
    result = db.fetchall()
    packed_files = {}
    for r in result:
        if r[0] not in packed_files:
            packed_files[r[0]] = []
        packed_files[r[0]].append(r[1])
    for pack_file, files in packed_files.items():
        pack_path_absolute = packed_base_path.joinpath(pack_file.strip('/'))
        is_tar = tarfile.is_tarfile(pack_path_absolute)
        if not is_tar:
            print(f'Skip file {pack_file}')
        with tarfile.open(pack_path_absolute, mode='r:gz') as tar:
            for f in files:
                member_info = tar.getmember(f.strip('/'))
                reader = tar.extractfile(member_info)
                file_output_path = unpack_base_path.joinpath(f.strip('/'))
                if file_output_path.exists():
                    print(f'File {f} already exists.')

                file_output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_output_path, mode='wb', buffering=1024 * 1024) as outfile:
                    outfile.write(reader.read())
                pass

    db.close()
