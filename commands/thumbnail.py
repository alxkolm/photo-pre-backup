import pathlib
import subprocess
from typing import Dict

import commands.thumbnail
import utils.file

import logging
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import configargparse
from config import options
import config

INPUT_DIRECTORY = config.options.input_dir
OUTPUT_DIRECTORY = config.options.output_dir


def run():
    with logging_redirect_tqdm():
        try:
            flist = list(utils.file.list_files(INPUT_DIRECTORY))

            # metadata = {fp:get_meta(fp) for fp in tqdm(flist)}
            thumbnails = {}
            for fp in tqdm(flist):
                thumbnails[fp] = create_thumbnail(fp)

            extool.terminate()
        except KeyboardInterrupt:
            logging.info('Interrupted by user. Bye!')
    pass


# Meta



def create_image_thumbnail(input_path: str, out_path: str) -> bool:
    shell_command = ['convert', '-resize', '300', '-quality', '50', input_path, out_path]
    x = subprocess.call(shell_command)
    return True if x == 0 else False


def create_video_thumbnail(input_path: str, out_path: pathlib.Path, meta: Dict) -> bool:
    shell_command = ['pyvideothumbnailer',
                     '--background-color', 'black',
                     '--header-font-color', 'white',
                     '--header-font', 'DejaVuSans.ttf',
                     '--timestamp-font', 'DejaVuSans.ttf',
                     '--comment-text', meta.get('relative_path', ''),
                     '--width', '1920',
                     '--columns', '5',
                     '--rows', '4',
                     '--skip-seconds', '0',
                     '--jpeg-quality', '50',
                     '--output-directory', str(out_path.parent),
                     input_path]
    x = subprocess.call(shell_command)
    return True if x == 0 else False


def create_thumbnail(filepath: str) -> Dict:
    inpath = filepath
    relative_path = str(inpath).replace(INPUT_DIRECTORY, '')
    base_output_path = pathlib.Path(OUTPUT_DIRECTORY)
    output_path = base_output_path.joinpath(pathlib.Path(relative_path.strip('/')))
    # create directory for the file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_extensions = ['.mp4', '.mov']
    # route to specific thumbnail creation function depending on file extension
    if output_path.suffix in video_extensions:
        output_path = output_path.with_suffix('.jpg')
        # result = generate_thumbnail(str(inpath), str(output_path), options)
        result = create_video_thumbnail(str(inpath), output_path, meta={'relative_path': relative_path})
    else:
        if output_path.exists():
            logging.info(f"Thumbnail for file {relative_path} already exists. Skip thumbnail generation")
            result = True
        else:
            result = create_image_thumbnail(inpath, str(output_path))
    return {'thumbnail_path': output_path, 'is_generated': result}
