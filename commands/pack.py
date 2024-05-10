import json
from pathlib import Path
import sqlite3
import logging

from commands.thumbnail import get_thumbnail_filepath
from utils.file import list_files, sha256
import config


def run():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    db.execute('SELECT original_file_path FROM backup WHERE is_packed = 0 ORDER BY original_file_path')
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
    buckets.append(current_bucket) # add last bucket

    for b in buckets:
        # TODO compress files
        pass

