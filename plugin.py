import asyncio
import json
import subprocess
import sys
import os
import time

from config import Config
from backend import BackendClient
from version import get_version
from devita.sfo import sfo

from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, Game, GameTime, LicenseInfo, LocalGame


class RPCS3Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.ColecoVision, get_version(), reader, writer, token)
        self.config = Config()
        self.backend_client = BackendClient(self.config)
        self.games = []
        self.local_games_cache = self.local_games_list()
        self.process = None
        self.running_game_id = None


    def get_game_path(self, game_id):

        for search in self.config.game_paths:
            search_dir = self.config.config2path(
                self.config.main_directory, 
                search)

            for game in os.listdir(search_dir):
                game_dir = os.path.join(search_dir, game)

                # Extra folder here.
                if 'disc' in search:
                    game_dir = os.path.join(game_dir, 'PS3_GAME')

                # Check that PARAM.SFO exists before loading it.
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

        user_path = self.config.config2path(
            self.config.main_directory, 
            self.config.user_path)

        username = ''
        with open(user_path) as username_file:
            username = username_file.read()

        user_data = {}
        user_data['username'] = username
        self.store_credentials(user_data)
        return Authentication('rpcs3_user', user_data['username'])


    async def launch_game(self, game_id):

        args = []

        rpcs3_exe = self.config.config2path(
            self.config.main_directory,
            self.config.exe_path)

        eboot_bin = os.path.join(
            self.get_game_path(game_id),
            'USRDIR', 
            'EBOOT.BIN')

        if self.config.no_gui:
            args.append('--no-gui')

        command = [rpcs3_exe, eboot_bin] + args
        self.process = subprocess.Popen(command)
        self.backend_client.start_game_time()
        self.running_game_id = game_id

        return


    # Only as placeholders so the feature is recognized
    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass


    async def prepare_game_times_context(self, game_ids):
        return self.get_game_times()


    async def get_game_time(self, game_id, context):
        game_time = context.get(game_id)
        return game_time


    def get_game_times(self):

        # Get the path of the game times file.
        base_path = os.path.dirname(os.path.realpath(__file__))
        game_times_path = '{}/game_times.json'.format(base_path)
        game_times = {}

        # If the file does not exist, create it with default values.
        if not os.path.exists(game_times_path):
            for game in self.games:

                game_time = {}
                game_id = str(game[0])
                game_time['name'] = game[1]
                game_time['time_played'] = 0
                game_time['last_time_played'] = None

                game_times[game_id] = game_time

            with open(game_times_path, 'w', encoding='utf-8') as game_times_file:
                json.dump(game_times, game_times_file, indent=4)

        # If (when) the file exists, read it and return the game times.  
        with open(game_times_path, 'r', encoding='utf-8') as game_times_file:
            game_times_json = json.load(game_times_file)

            for game_time in game_times_json:

                # Each entry is actually the game ID.
                game_id = game_time

                time_played = game_times_json.get(game_time).get('time_played')
                last_time_played = game_times_json.get(game_time).get('last_time_played')
                
                game_times[game_id] = GameTime(game_id, time_played, last_time_played)

        return game_times


    def local_games_list(self):
        local_games = []

        for game in self.games:
            local_games.append(LocalGame(
                game[0],
                LocalGameState.Installed))

        return local_games


    def tick(self):
        try:
            if self.process.poll() is not None:

                self.backend_client.end_game_time()
                self.update_json_game_time(
                    self.running_game_id,
                    self.backend_client.get_session_duration(),
                    int(time.time()))

                self.process = None
                self.running_game_id = None

        except AttributeError:
            pass

        self.create_task(self.update_galaxy_game_times(), 'Update Galaxy game times')
        self.create_task(self.update_local_games(), 'Update local games')


    async def update_local_games(self):
        loop = asyncio.get_running_loop()

        new_list = await loop.run_in_executor(None, self.local_games_list)
        notify_list = self.backend_client.get_state_changes(self.local_games_cache, new_list)
        self.local_games_cache = new_list
        
        for local_game_notify in notify_list:
            self.update_local_game_status(local_game_notify)


    async def update_galaxy_game_times(self):

        # Leave time for Galaxy to fetch games before updating times
        await asyncio.sleep(60) 
        loop = asyncio.get_running_loop()

        game_times = await loop.run_in_executor(None, self.get_game_times)
        for game_time in game_times:
            self.update_game_time(game_time)


    def update_json_game_time(self, game_id, duration, last_time_played):

        # Get the path of the game times file.
        base_path = os.path.dirname(os.path.realpath(__file__))
        game_times_path = '{}/game_times.json'.format(base_path)
        game_times_json = None

        with open(game_times_path, 'r', encoding='utf-8') as game_times_file:
            game_times_json = json.load(game_times_file)

        old_time_played = game_times_json.get(game_id).get('time_played')

        new_time_played = old_time_played + duration

        game_times_json[game_id]['time_played'] = new_time_played
        game_times_json[game_id]['last_time_played'] = last_time_played

        with open(game_times_path, 'w', encoding='utf-8') as game_times_file:
            json.dump(game_times_json, game_times_file, indent=4)

        self.update_game_time(GameTime(game_id, new_time_played, last_time_played))


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
