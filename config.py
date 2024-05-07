import configargparse

parser = configargparse.ArgParser(
    default_config_files=['photo-backup.conf']
)

parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
# parser.add_argument('command')
parser.add_argument('--base-dir', required=True)
parser.add_argument('--input-dir', required=True)
parser.add_argument('--output-dir', required=True)

subparser_command = parser.add_subparsers(title='command', help='Operation mode', dest='command')
subparser_command.add_parser('thumbnail')
subparser_index = subparser_command.add_parser('index')

subparser_index_command = subparser_index.add_subparsers(title='subcommand', dest='subcommand')
subparser_index_command.default = 'list'
subparser_index_command.add_parser('list')
subparser_index_command.add_parser('update')


options = parser.parse_args()
pass
