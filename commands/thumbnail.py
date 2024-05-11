import logging
import pathlib
import subprocess
from typing import Dict

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

import config
import utils.file

video_extensions = ['.mp4', '.mov']


def run():
    with logging_redirect_tqdm():
        try:
            flist = list(utils.file.list_files(config.options.photo_dir))

            # metadata = {fp:get_meta(fp) for fp in tqdm(flist)}
            thumbnails = {}
            for fp in tqdm(flist):
                thumbnails[fp] = create_thumbnail(fp)

            # extool.terminate()
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


def get_thumbnail_filepath(filepath: str) -> str:
    inpath = filepath
    relative_path = str(inpath).replace(config.options.photo_dir, '')
    base_output_path = pathlib.Path(config.options.thumbnails_dir)
    output_path = base_output_path.joinpath(pathlib.Path(relative_path.strip('/')))
    if output_path.suffix in video_extensions:
        output_path = output_path.with_suffix(f'{output_path.suffix}.jpg')
    return output_path


def create_thumbnail(filepath: str) -> Dict:
    inpath = filepath
    output_path = get_thumbnail_filepath(filepath)
    # create directory for the file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    relative_path = str(inpath).replace(config.options.photo_dir, '')

    # route to specific thumbnail creation function depending on file extension
    if output_path.suffix in video_extensions:
        output_path = output_path.with_suffix(f'{output_path.suffix}.jpg')
        # result = generate_thumbnail(str(inpath), str(output_path), options)
        result = create_video_thumbnail(str(inpath), output_path, meta={'relative_path': relative_path})
    else:
        if output_path.exists():
            logging.info(f"Thumbnail for file {relative_path} already exists. Skip thumbnail generation")
            result = True
        else:
            result = create_image_thumbnail(inpath, str(output_path))
    return {'thumbnail_path': output_path, 'is_generated': result}
