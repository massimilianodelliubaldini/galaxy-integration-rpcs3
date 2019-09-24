import asyncio
import json
import subprocess
import sys
import os
import time

import trophy
from trophy import Trophy
from config import Config
from backend import BackendClient
from version import get_version

from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, Game, GameTime, LicenseInfo, LocalGame, Achievement


class RPCS3Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.ColecoVision, get_version(), reader, writer, token)
        self.config = Config()
        self.backend_client = BackendClient(self.config)
        self.games = []
        self.local_games_cache = self.local_games_list()
        self.process = None
        self.running_game_id = None


    async def authenticate(self, stored_credentials=None):
        return self.do_auth()


    async def pass_login_credentials(self, step, credentials, cookies):
        return self.do_auth()


    def do_auth(self):

        username = ''
        with open(self.config.localusername, 'r') as username_file:
            username = username_file.read()

        user_data = {}
        user_data['username'] = username
        self.store_credentials(user_data)
        return Authentication('rpcs3_user', user_data['username'])


    async def launch_game(self, game_id):

        args = []
        eboot_bin = self.config.joinpath(
            self.backend_client.get_game_path(game_id),
            'USRDIR', 
            'EBOOT.BIN')

        if self.config.no_gui:
            args.append('--no-gui')

        command = [self.config.rpcs3_exe, eboot_bin] + args
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
        return self.get_game_times(game_ids)


    async def prepare_achievements_context(self, game_ids):
        return self.get_trophy_achs()


    async def get_game_time(self, game_id, context):
        game_time = context.get(game_id)
        return game_time


    async def get_unlocked_achievements(self, game_id, context):
        achs = context.get(game_id)
        return achs    


    def get_game_times(self, game_ids):

        # Get the path of the game times file.
        base_path = os.path.dirname(os.path.realpath(__file__))
        game_times_path = os.path.join(base_path, 'game_times.json')
        game_times = {}

        # If the file does not exist, create it with default values.
        if not os.path.exists(game_times_path):
            for game in self.games:

                game_id = str(game[0])
                game_times[game_id] = GameTime(game_id, 0, None)

            with open(game_times_path, 'w', encoding='utf-8') as game_times_file:
                json.dump(game_times, game_times_file, indent=4)

        # If (when) the file exists, read it and return the game times.  
        with open(game_times_path, 'r', encoding='utf-8') as game_times_file:
            game_times_json = json.load(game_times_file)

            for game_id in game_times_json:
                if game_id in game_ids:
                    time_played = game_times_json.get(game_id).get('time_played')
                    last_time_played = game_times_json.get(game_id).get('last_time_played')

                    game_times[game_id] = GameTime(game_id, time_played, last_time_played)

        return game_times

    def get_trophy_achs(self):

        game_ids = []
        for game in self.games:
            game_ids.append(game[0])

        trophies = None
        all_achs = {}
        for game_id in game_ids:
            game_path = self.backend_client.get_game_path(game_id)

            try:
                trophies = Trophy(self.config, game_path)
                keys = trophies.tropusr.table6.keys()

                game_achs = []
                for key in keys:
                    ach = trophies.trop2ach(key)
                    if ach is not None:
                        game_achs.append(trophies.trop2ach(key))

                all_achs[game_id] = game_achs

            # If tropusr doesn't exist, this game has no trophies.
            except AttributeError:
                all_achs[game_id] = []

        return all_achs


    def tick(self):
        try:
            if self.process.poll() is not None:

                self.backend_client.end_game_time()
                self.update_json_game_time(
                    self.running_game_id,
                    self.backend_client.get_session_duration(),
                    int(time.time()))
    
                # Only update recently played games. Updating all game times every second fills up log way too quickly.
                self.create_task(self.update_galaxy_game_times(self.running_game_id), 'Update Galaxy game times')

                self.process = None
                self.running_game_id = None

        except AttributeError:
            pass

        self.create_task(self.update_local_games(), 'Update local games')
        self.create_task(self.update_achievements(), 'Update achievements')


    async def update_local_games(self):
        loop = asyncio.get_running_loop()

        new_list = await loop.run_in_executor(None, self.local_games_list)
        notify_list = self.backend_client.get_state_changes(self.local_games_cache, new_list)
        self.local_games_cache = new_list
        
        for local_game_notify in notify_list:
            self.update_local_game_status(local_game_notify)


    async def update_galaxy_game_times(self, game_id):

        # Leave time for Galaxy to fetch games before updating times
        await asyncio.sleep(60) 
        loop = asyncio.get_running_loop()

        game_times = await loop.run_in_executor(None, self.get_game_times, [game_id])
        for game_id in game_times:
            self.update_game_time(game_times[game_id])


    async def update_achievements(self):

        # Leave time for Galaxy to fetch games before updating times
        await asyncio.sleep(60) 
        loop = asyncio.get_running_loop()

        achs = await loop.run_in_executor(None, self.get_trophy_achs)
        # for ach in achs:
            # self.unlock_achievement(ach) # TODO - how/when to handle this?


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


    def local_games_list(self):
        local_games = []

        for game in self.games:
            local_games.append(LocalGame(
                game[0],
                LocalGameState.Installed))

        return local_games


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
