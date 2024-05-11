import json
import pathlib
import sqlite3

from commands.thumbnail import get_thumbnail_filepath
from utils.file import list_files, sha256
import config
from utils.exiftool import get_meta


def run():
    # command routing
    routing = {
        'list': run_list,
        'update': run_update
    }

    if config.options.subcommand not in routing:
        print(f"Unknown sub-command for command `index`: {config.options.subcommand}")
        exit(1)

    routed_function = routing[config.options.subcommand]
    routed_function()


def run_list():
    fs = list_files(config.options.input_dir)
    for x in fs:
        print(x)


def run_update():
    # open or create sqlite database
    # scan files and add all new files to database
    # * scan thumbnails too
    conn = sqlite3.connect(config.options.index_file)
    db = conn.cursor()

    def db_initialization():
        """Initialize DB if it is empty"""
        cursor = db.execute("""
        CREATE TABLE IF NOT EXISTS backup (
            original_file_path TEXT UNIQUE,
            is_packed INTEGER NOT NULL,
            has_thumbnail INTEGER NOT NULL,
            has_exif INTEGER NOT NULL,
            packed_file_path TEXT NULL,
            thumbnail_file_path TEXT NULL,
            exif TEXT NULL,
            file_checksum TEXT
        )
        """)

    def update_index():
        fs = list_files(config.options.photo_dir)
        for filepath in list(fs)[0:100]:
            exifmeta = get_meta(filepath)
            exifmeta = None if 'error' in exifmeta else exifmeta
            relative_path = str(filepath).replace(config.options.photo_dir, '')
            thumbnail_path = pathlib.Path(get_thumbnail_filepath(filepath))
            thumbnail_path_relative = str(thumbnail_path).replace(config.options.thumbnails_dir, '')
            has_thumbnail = thumbnail_path.exists()

            params = [(str(relative_path),
                       0,
                       1 if has_thumbnail else 0,
                       1 if exifmeta else 0,
                       # None,
                       str(thumbnail_path_relative) if has_thumbnail else None,
                       json.dumps(exifmeta) if exifmeta else None,
                       sha256(filepath))]
            db.executemany("""
            INSERT INTO backup (original_file_path,is_packed,has_thumbnail,has_exif, thumbnail_file_path,exif, file_checksum)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT (original_file_path) DO UPDATE SET
                -- is_packed          = excluded.is_packed,
                has_thumbnail      = excluded.has_thumbnail,
                has_exif           = excluded.has_exif,
                -- packed_file_path   = excluded.packed_file_path,
                thumbnail_file_path= excluded.thumbnail_file_path,
                exif               = excluded.exif,
                file_checksum      = excluded.file_checksum
            """, params)
        conn.commit()

    db_initialization()
    update_index()
    conn.close()
