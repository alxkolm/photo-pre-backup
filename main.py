# sudo apt-get install -y libmediainfo-dev

import commands.thumbnail
import commands.the_index
import logging
from config import options

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # command routing
    routing = {
        'thumbnail': commands.thumbnail.run,
        'index': commands.the_index.run
    }

    if options.command not in routing:
        print(f"Unknown command: {options.command}")
        exit(1)

    routed_function = routing[options.command]
    routed_function()
