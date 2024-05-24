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
        'index': run_status,
        'parts': status_parts,
        'check': status_check,
    }

    if config.options.subcommand not in routing:
        print(f"Unknown sub-command for command `status`: {config.options.subcommand}")
        exit(1)

    routed_function = routing[config.options.subcommand]
    routed_function()


def run_status():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()
    SQL_STATS = """
    SELECT count(1) AS count_total,
       count(iif(has_thumbnail,1,NULL)) AS count_has_thumbnails,
       count(iif(has_exif,1,NULL)) AS count_has_exif,
       count(iif(is_packed,1,NULL)) AS count_is_packed,
       count(DISTINCT packed_file_path)
    FROM backup
    """
    db.execute(SQL_STATS)
    stats_data = db.fetchone()


    # Check existing of thumbnails
    db.execute("""
    SELECT original_file_path,
           thumbnail_file_path,
           packed_file_path,
           is_packed
    FROM backup
    ORDER BY thumbnail_file_path
    """)
    result = db.fetchall()

    thumb_base_dir = Path(config.options.thumbnails_dir)
    thumb_existed_count = 0
    thumb_non_existed_count = 0

    # check thumbnails
    for record_info in result:
        if record_info[1] is None:
            continue
        thumb_absolute_path = thumb_base_dir.joinpath(record_info[1].strip('/'))

        if thumb_absolute_path.exists():
            thumb_existed_count += 1
        else:
            thumb_non_existed_count += 1

    packed_base_dir = Path(config.options.packed_dir)
    packed_file_exist_count = 0
    packed_file_non_exist_count = 0

    # check compressed files
    for record_info in result:
        if record_info[2] is None:
            continue
        is_packed = record_info[3]
        packed_file_absolute_path = packed_base_dir.joinpath(record_info[2].strip('/'))
        if packed_file_absolute_path.exists():
            packed_file_exist_count += 1
        elif is_packed:
            packed_file_non_exist_count += 1

    stats = {
        'Total files in database': stats_data[0],
        'Files with thumbnails': stats_data[1],
        'Files with EXIF data': stats_data[2],
        'Number of packed files': stats_data[3],
        'Number of files in existed archives': packed_file_exist_count,
        'Number of files in non existed archives': packed_file_non_exist_count,
        'Number of archives': stats_data[4],
        'Number of valid thumbnails': thumb_existed_count,
        'Number of broken thumbnails': thumb_non_existed_count,

    }
    max_name_width = max([len(x) for x in stats.keys()])
    for name, value in stats.items():
        print(f"{name:<{max_name_width}}\t{value}")


def status_parts():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    SQL = """
    SELECT packed_file_path, original_file_path
    FROM backup
    WHERE is_packed = 1
    ORDER BY packed_file_path,original_file_path
    """

    db.execute(SQL)
    result = db.fetchall()

    packed_base_dir = Path(config.options.packed_dir)
    parts_stats = {}
    for row in result:
        part_file = row[0]
        if part_file not in parts_stats:
            parts_stats[part_file] = {
                'exists': None,
                'files_count': 0
            }
        part_path =packed_base_dir.joinpath(part_file.strip('/'))

        if parts_stats[part_file]['exists'] is None:
            parts_stats[part_file]['exists'] = part_path.exists()
        parts_stats[part_file]['files_count'] += 1

    max_name_width = max([len(x) for x in parts_stats.keys()]) if len(parts_stats) > 0 else 0
    for part_file, stats in parts_stats.items():
        print(f'{part_file:<{max_name_width}}\texists={stats["exists"]}\t{stats["files_count"]} files')


def status_check():
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    db.execute('SELECT original_file_path, file_checksum FROM backup')
    # create map with file => checksum
    checksums = {x[0]: x[1] for x in db.fetchall()}

    photo_base_path = Path(config.options.photo_dir)
    packed_base_path = Path(config.options.packed_dir)
    fs = list_files(config.options.photo_dir)
    changed_files = {}
    file_count = 0
    for filepath in tqdm(list(fs)):
        relative_path = str(filepath).replace(config.options.photo_dir, '')
        actual_checksum = sha256(filepath)
        if (actual_checksum != checksums[relative_path]):
            changed_files[relative_path] = {
                'actual_checksum': actual_checksum,
                'expected_checksum': checksums[relative_path]
            }
        file_count += 1
    if len(changed_files) == 0:
        print(f'Checked {file_count} files. Found {len(changed_files)} changed files. Everything is OK.')
    else:
        for f, info in changed_files.items():
            print(f)