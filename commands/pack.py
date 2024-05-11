import logging
import sqlite3
import tarfile
from pathlib import Path

from uuid_extensions import uuid7

import config


def run():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    db.execute('SELECT original_file_path FROM backup WHERE is_packed = 0 AND has_thumbnail = 1 ORDER BY original_file_path')
    photo_path = Path(config.options.photo_dir)
    total = 0
    files_info = []
    # infer files info
    for x in db.fetchall():
        absolute_path = photo_path.joinpath(Path(x[0].strip('/')))
        size = absolute_path.stat().st_size
        logging.info(f'Process {absolute_path} ({size} bytes)')
        files_info.append({
            'original_file_path': x[0],
            'absolute_path': absolute_path,
            'size': size
        })
        total = total + size
    logging.info(f"Found {len(files_info)} files with total size {total/1024/1024:.1f} Mb")
    buckets = []
    current_buckets_size = 0
    current_bucket = []
    for x in files_info:
        if current_buckets_size >= 128 * 1024 * 1024:
            buckets.append(current_bucket)
            current_bucket = []
            current_buckets_size = 0
        current_bucket.append(x)
        current_buckets_size = current_buckets_size + x['size']
    if len(current_bucket) > 0:
        buckets.append(current_bucket)  # add last bucket

    output_base_path = Path(config.options.packed_dir)
    output_base_path.mkdir(parents=True, exist_ok=True)

    for files in buckets:
        # TODO compress files
        # part_path = Path('{0}.tar.gz'.format(uuid.uuid1(0, int(time.time())).hex))
        part_path = Path('{0}.tar.gz'.format(uuid7(as_type='str')))
        full_path = output_base_path.joinpath(part_path)
        with tarfile.open(full_path, mode='w:gz', compresslevel=1) as targz:
            for file in files:
                targz.add(file['absolute_path'], arcname=file['original_file_path'])
        SQL = "UPDATE backup SET is_packed = 1, packed_file_path = ? WHERE original_file_path = ?"
        db.executemany(SQL, [(str(part_path), str(x['original_file_path'])) for x in files])
        db.connection.commit()
