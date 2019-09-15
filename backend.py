import json
import os
import sys

from config import Config
from devita.sfo import sfo

class BackendClient:
    def __init__(self, config):
        self.config = config


    # Returns an array of Title ID, Title pairs.
    def get_games(self):

        # May still be useful if more info on a game is needed.
        # url = 'https://rpcs3.net/compatibility?api=v1&g='

        results = []

        for search in self.config.game_paths:
            search_dir = self.config.config2path(
                self.config.main_directory, 
                search)

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
