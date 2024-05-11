import configargparse

parser = configargparse.ArgParser(
    default_config_files=['photo-backup.conf']
)

parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')

parser.add_argument('--index-file', required=True)
parser.add_argument('--photo-dir', required=True)
parser.add_argument('--thumbnails-dir', required=True)
parser.add_argument('--packed-dir', required=True)

subparser_command = parser.add_subparsers(title='command', help='Operation mode', dest='command')
thumbnail = subparser_command.add_parser('thumbnail')
index = subparser_command.add_parser('index')
pack = subparser_command.add_parser('pack')

index_command = index.add_subparsers(title='subcommand', dest='subcommand')
index_command.default = 'list'
index_command.add_parser('list')
index_command.add_parser('update')

options = parser.parse_args()
pass
