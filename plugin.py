import asyncio
import json
import subprocess
import sys
import os

import config
from backend import BackendClient
from version import __version__
from devita.sfo import sfo

from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, Game, GameTime, LicenseInfo, LocalGame


class RPCS3Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.ColecoVision, __version__, reader, writer, token)
        self.backend_client = BackendClient()
        self.games = []
        self.local_games_cache = self.local_games_list()


    def config2path(self, path, *paths):
        return os.path.normpath(os.path.join(path, *paths))


    def get_game_path(self, game_id):

        for search in config.game_paths:
            search_dir = self.config2path(config.main_directory, search)

            for game in os.listdir(search_dir):
                game_dir = os.path.join(search_dir, game)

                # Extra folder here.
                if 'disc' in search:
                    game_dir = os.path.join(game_dir, 'PS3_GAME')

                sfo_path = os.path.join(game_dir, 'PARAM.SFO')
                if os.path.exists(sfo_path):
                    param_sfo = sfo(sfo_path)

                    # PARAM.SFO is read as a binary file,
                    # so all keys must also be in binary.
                    if bytes(game_id, 'utf-8') in param_sfo.params[bytes('TITLE_ID', 'utf-8')]:
                        return game_dir


    async def authenticate(self, stored_credentials=None):
        return self.do_auth()


    async def pass_login_credentials(self, step, credentials, cookies):
        return self.do_auth()


    def do_auth(self):

        user_path = self.config2path(
            config.main_directory, 
            config.user_path)

        username = ''
        with open(user_path) as username_file:
            username = username_file.read()

        user_data = {}
        user_data['username'] = username
        self.store_credentials(user_data)
        return Authentication('rpcs3_user', user_data['username'])


    async def launch_game(self, game_id):

        rpcs3_exe = self.config2path(
            config.main_directory,
            config.exe_path)

        eboot_bin = os.path.join(
            self.get_game_path(game_id),
            'USRDIR', 
            'EBOOT.BIN')

        subprocess.Popen([rpcs3_exe, eboot_bin])
        return


    # Only as placeholders so the feature is recognized
    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass


    async def prepare_game_times_context(self, game_ids):
        return self.get_games_times_dict()


    async def get_game_time(self, game_id, context):
        game_time = context.get(game_id)
        return game_time


    def get_games_times_dict(self):

        # Get the directory of this file and format it to
        # have the path to the game times file
        base_dir = os.path.dirname(os.path.realpath(__file__))
        game_times_path = '{}/game_times.json'.format(base_dir)

        # Check if the file exists
        # If not create it with the default value of 0 minutes played
        if not os.path.exists(game_times_path):
            game_times_dict = {}
            for game in self.games:
                entry = {}
                id = str(game[0])
                entry['name'] = game[1]
                entry['time_played'] = 0
                entry['last_time_played'] = 0
                game_times_dict[id] = entry

            with open(game_times_path, 'w') as game_times_file:
                json.dump(game_times_dict, game_times_file, indent=4)

        # Once the file exists read it and return the game times    
        game_times = {}

        with open(game_times_path, 'r') as game_times_file:
            parsed_game_times_file = json.load(game_times_file)

            for entry in parsed_game_times_file:
                game_id = entry
                time_played = int(parsed_game_times_file.get(entry).get('time_played'))
                last_time_played = int(parsed_game_times_file.get(entry).get('last_time_played'))
                
                game_times[game_id] = GameTime(
                    game_id,
                    time_played,
                    last_time_played)

        return game_times


    def local_games_list(self):
        local_games = []

        for game in self.games:
            local_games.append(LocalGame(
                game[0],
                LocalGameState.Installed))

        return local_games


    def tick(self):

        async def update_local_games():
            loop = asyncio.get_running_loop()
            new_local_games_list = await loop.run_in_executor(None, self.local_games_list)
            notify_list = self.backend_client.get_state_changes(self.local_games_cache, new_local_games_list)
            self.local_games_cache = new_local_games_list
            
            for local_game_notify in notify_list:
                self.update_local_game_status(local_game_notify)

        asyncio.create_task(update_local_games())


    async def get_owned_games(self):
        self.games = self.backend_client.get_games()
        owned_games = []
        
        for game in self.games:
            owned_games.append(Game(
                game[0],
                game[1],
                None,
                LicenseInfo(LicenseType.SinglePurchase, None)))
            
        return owned_games


    async def get_local_games(self):
        return self.local_games_cache


def main():
    create_and_run_plugin(RPCS3Plugin, sys.argv)


# run plugin event loop
if __name__ == '__main__':
    main()
