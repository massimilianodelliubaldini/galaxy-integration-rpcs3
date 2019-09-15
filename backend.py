import json
import os
import sys

import config
from devita.sfo import sfo

class BackendClient:
    def __init__(self):
        pass

    def config2path(self, path, *paths):
        return os.path.normpath(os.path.join(path, *paths))

    def get_games(self):
        # url = 'https://rpcs3.net/compatibility?api=v1&g='
        results = []

        for search_path in config.game_paths:
            game_path = self.config2path(config.main_directory, search_path)

            for root, dirs, files in os.walk(game_path):
                for file in files:
                    if file == 'EBOOT.BIN':

                        bottom_path = os.path.join(root, file)
                        sfo_path = bottom_path.replace(
                            os.path.join('USRDIR', 'EBOOT.BIN'), 
                            'PARAM.SFO')

                        # PARAM.SFO is read as a binary file,
                        # so all keys must also be in binary.
                        param_sfo = sfo(sfo_path)
                        title_id = param_sfo.params[bytes('TITLE_ID', 'utf-8')]
                        title = param_sfo.params[bytes('TITLE', 'utf-8')]

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
