import datetime
import logging
import sqlite3
import tarfile
from pathlib import Path

from uuid_extensions import uuid7

import config


def run():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    db.execute('SELECT original_file_path, mime_type FROM backup WHERE is_packed = 0 AND has_thumbnail = 1 ORDER BY original_file_path')
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
            'mime_type': x[1],
            'absolute_path': absolute_path,
            'size': size
        })
        total = total + size
    logging.info(f"Found {len(files_info)} files with total size {total/1024/1024:.1f} Mb")

    # split list of files to two subsets: images and video
    is_video = lambda z: z['mime_type'].startswith('video')
    buckets_video = split_on_buckets([x for x in files_info if is_video(x)])
    buckets_misc = split_on_buckets([x for x in files_info if not is_video(x)])
    compress_buckets(buckets_misc, 'misc')
    compress_buckets(buckets_video, 'video')


def split_on_buckets(files_info):
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
    return buckets


def compress_buckets(buckets, filename_suffix):
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    output_base_path = Path(config.options.packed_dir)
    output_base_path.mkdir(parents=True, exist_ok=True)
    for files in buckets:
        # TODO compress files
        # part_path = Path('{0}.tar.gz'.format(uuid.uuid1(0, int(time.time())).hex))
        part_path = Path('{0}_{1}.tar.gz'.format(uuid7(as_type='str'), filename_suffix))
        month = datetime.date.today().strftime('%Y-%m')
        full_path = output_base_path.joinpath(month, part_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(full_path, mode='w:gz', compresslevel=1) as targz:
            for file in files:
                targz.add(file['absolute_path'], arcname=file['original_file_path'])
        SQL = "UPDATE backup SET is_packed = 1, packed_file_path = ? WHERE original_file_path = ?"
        db.executemany(SQL, [(str(part_path), str(x['original_file_path'])) for x in files])
        db.connection.commit()
