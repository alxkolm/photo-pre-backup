import configargparse

parser = configargparse.ArgParser(
    default_config_files=['photo-backup.conf']
)

parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
parser.add_argument('command')
parser.add_argument('--input-dir', required=True)
parser.add_argument('--output-dir', required=True)

options = parser.parse_args()
