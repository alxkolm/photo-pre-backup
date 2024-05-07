import json
import sqlite3
from utils.file import list_files
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
    conn = sqlite3.connect(f'{config.options.base_dir}/index.db')
    db = conn.cursor()

    def db_initialization():
        """Initialize DB if it is empty"""
        cursor = db.execute("""
        CREATE TABLE IF NOT EXISTS backup (
            original_file_path TEXT UNIQUE,
            is_packed INTEGER,
            has_thumbnail INTEGER,
            has_exif INTEGER,
            packed_file_path TEXT NULL,
            thumbnail_file_path TEXT NULL,
            exif TEXT NULL
        )
        """)

    def update_index():
        fs = list_files(config.options.input_dir)
        for x in fs:
            exifmeta = get_meta(x)
            exifmeta = None if 'error' in exifmeta else exifmeta
            db.executemany("""
            INSERT INTO backup (original_file_path,is_packed,has_thumbnail,has_exif, packed_file_path,thumbnail_file_path,exif) VALUES (?,?,?,?,?,?,?)
            """, [(str(x), 0, 0, 1 if exifmeta else 0, None, None, json.dumps(exifmeta) if exifmeta else None)])
        conn.commit()

    db_initialization()
    update_index()
    conn.close()
