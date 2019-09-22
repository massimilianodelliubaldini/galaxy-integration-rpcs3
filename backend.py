import os
import sys
import time
import yaml
import json

from config import Config
from devita.sfo import sfo

class BackendClient:
    def __init__(self, config):
        self.config = config
        self.start_time = 0
        self.end_time = 0


    # Returns an array of Title ID, Title pairs.
    def get_games(self):

        # May still be useful if more info on a game is needed.
        # url = 'https://rpcs3.net/compatibility?api=v1&g='

        results = []
        game_paths = []
        with open(self.config.games_yml) as games_file:

            games_yml = yaml.load(games_file, Loader=yaml.SafeLoader)
            for game in games_yml:
                game_paths.append(games_yml[game])

        game_paths.append(self.config.game_directory)

        # This is probably crazy inefficient.
        for search_dir in game_paths:
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file == 'EBOOT.BIN':

                        # Search for EBOOT.BIN to find actual games,
                        # then PARAM.SFO is one level up from EBOOT.BIN.
                        bin_path = os.path.join(root, file)
                        sfo_path = bin_path.replace(
                            os.path.join('USRDIR', 'EBOOT.BIN'), 
                            'PARAM.SFO')

                        # PARAM.SFO is read as a binary file,
                        # so all keys must also be in binary.
                        param_sfo = sfo(sfo_path)
                        title_id = param_sfo.params[bytes('TITLE_ID', 'utf-8')]
                        title = param_sfo.params[bytes('TITLE', 'utf-8')]

                        # Convert results to strings before return.
                        results.append([
                            str(title_id, 'utf-8'), 
                            str(title, 'utf-8')])

        return results


    def get_game_path(self, game_id):
        
        with open(self.config.games_yml) as games_file:
            games_yml = yaml.load(games_file, Loader=yaml.SafeLoader)
            try:
                game_path = games_yml[game_id]
                game_path = os.path.join(game_path, 'PS3_GAME')
                return game_path

            # If the game is not found in games.yml, we will search config.game_path.
            except KeyError:
                pass

        for folder in os.listdir(self.config.game_directory):
            check_path = os.path.join(self.config.game_directory, folder)

            # Check that PARAM.SFO exists before loading it.
            sfo_path = os.path.join(check_path, 'PARAM.SFO')
            if os.path.exists(sfo_path):
                param_sfo = sfo(sfo_path)

                # If PARAM.SFO contains game_id, we found the right path.
                if bytes(game_id, 'utf-8') in param_sfo.params[bytes('TITLE_ID', 'utf-8')]:
                    return check_path

        # If we manage to get here, we should really raise an exception.
        raise FileNotFoundError


    def get_state_changes(self, old_list, new_list):
        old_dict = {x.game_id: x.local_game_state for x in old_list}
        new_dict = {x.game_id: x.local_game_state for x in new_list}
        result = []

        # removed games
        result.extend(LocalGame(id, LocalGameState.None_) for id in old_dict.keys() - new_dict.keys())
        
        # added games
        result.extend(local_game for local_game in new_list if local_game.game_id in new_dict.keys() - old_dict.keys())
        
        # state changed
        result.extend(LocalGame(id, new_dict[id]) for id in new_dict.keys() & old_dict.keys() if new_dict[id] != old_dict[id])
        
        return result


    def start_game_time(self):
        self.start_time = time.time()


    def end_game_time(self):
        self.end_time = time.time()


    def get_session_duration(self):
        delta = self.end_time - self.start_time
        minutes = int(round(delta / 60))
        return minutes