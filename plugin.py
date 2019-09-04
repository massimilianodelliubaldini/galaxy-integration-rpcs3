import sys
import os
import json
import subprocess

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LocalGameState
from galaxy.api.types import Game, LocalGame

class RPCS3Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.Generic, # PS3 is not a supported platform yet.
            __version__
            reader,
            writer,
            token
        )

    ### Authentication ###
        
    async def authenticate(self, stored_credentials=None):
        pass

    async def pass_login_credentials(self, step, credentials, cookies):
        pass

    ### Platform ###

    async def launch_platform_client(self):
        pass

    async def shutdown_platform_client(self):
        pass

    ### Library Management ###

    async def get_owned_games(self):
        pass

    async def get_local_games(self):
        pass

    ### Game Management ###

    async def launch_game(self, game_id):
        pass

    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass

    async def get_game_time(self, game_id, context):
        pass

    ### Trophies ###

    async def get_unlocked_achievements(self, game_id, context):
        pass

    ### Friends ###

    async def get_friends(self):
        pass

def main():
    create_and_run_plugin(RPCS3Plugin, sys.argv)

# run plugin event loop
if __name__ == "__main__":
    main()
