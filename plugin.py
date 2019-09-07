import sys
import os
import json
import subprocess
import re
import requests

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LocalGameState
from galaxy.api.types import Game, LocalGame
from version import __version__

class RPCS3Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.ColecoVision, # PS3 is not a supported platform yet.
            __version__,
            reader,
            writer,
            token)

    def tick(self):
        pass
        
    ### Authentication ###
        
    async def authenticate(self, stored_credentials=None):
        return self.handle_auth()

    async def pass_login_credentials(self, step, credentials, cookies):
        return self.handle_auth()

    def handle_auth(self):

        with open('config.json') as config_file:
            config = json.load(config_file)

        username_filename = json2path(
            config['rpcs3']['home'], 
            config['user']['home'], 
            config['user']['namefile'])

        with open(username_filename) as username_file:
            username = username_file.read()

        user_data = {}
        user_data["username"] = username
        self.store_credentials(user_data)
        return Authentication("rpcs3_user", user_data["username"])

    ### Library Management ###

    async def get_local_games(self):

        url = 'https://rpcs3.net/compatibility?api=v1&g='
        owned_games = []

        with open('config.json') as config_file:
            config = json.load(config_file)

        games_filename = json2path(
            config['rpcs3']['home'], 
            config['rpcs3']['games'])

        with open(games_filename) as games_file: 
            game_ids = re.findall('\w+(?=: .*)', games_file.read())


        for game_id in game_ids:
            page = requests.get(url + game_id)
            game = json.loads(page.text)['results'][game_id]

            owned_games.append(Game(
                game_id, 
                game['title'], 
                None, 
                LicenseInfo(LicenseType.SinglePurchase, None)))

        return owned_games

    async def get_owned_games(self):
        return self.get_local_games()

    ### Game Management ###

    async def launch_game(self, game_id):

        with open('config.json') as config_file:
            config = json.load(config_file)

        rpcs3_exe = json2path(
            config['rpcs3']['home'], 
            config['rpcs3']['exe'])

        eboot_bin = os.path.join(
            get_game_path(game_id), 
            'PS3_GAME', 
            'USRDIR', 
            'EBOOT.BIN')

        subprocess.Popen([rpcs3_exe, eboot_bin])
        return

    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass

    async def get_game_time(self, game_id, context):
        game_time = context.get(game_id)
        return game_time

    ### Trophies ###

    async def get_unlocked_achievements(self, game_id, context):
        return

    ### Helpers and Miscellaneous ###

    def json2path(path, *paths):
        return os.path.normpath(os.path.join(path, *paths))

    def get_game_path(game_id):

        game_path = ''
        with open('config.json') as config_file:
            config = json.load(config_file)

        disc_games = json2path(
            config['rpcs3']['home'],
            config['library']['disc'])

        for d in os.listdir(disc_games):
            disc_dir = os.path.join(disc_games, d)
            param_sfo = os.path.join(disc_dir, 'PS3_GAME', 'PARAM.SFO')

            with open(param_sfo) as param_file:
                if game_id in param_file:
                    game_path = disc_dir

        return game_path


def main():
    create_and_run_plugin(RPCS3Plugin, sys.argv)

# run plugin event loop
if __name__ == "__main__":
    main()
