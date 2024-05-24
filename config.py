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
unpack = subparser_command.add_parser('unpack')
status = subparser_command.add_parser('status')
cleanup = subparser_command.add_parser('cleanup')

unpack.add_argument('path', default='*', nargs='?')

index_command = index.add_subparsers(title='subcommand', dest='subcommand')
index_command.default = 'list'
index_list = index_command.add_parser('list')
index_command.add_parser('update')

index_list.add_argument('path', default='*', nargs='?')
index_list.add_argument('--packs', required=False, action='store_true')

status_command = status.add_subparsers(title='subcommand', dest='subcommand')
status_command.default = 'index'
status_command.add_parser('index')
status_command.add_parser('parts')
status_command.add_parser('check')

cleanup_command = cleanup.add_subparsers(title='subcommand', dest='subcommand')
cleanup_command.default = 'remove'

options = parser.parse_args()
pass
