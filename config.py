# Make sure to use / instead of \ in file paths.
import os

class Config:
    def __init__(self):

        # Point this to the RPCS3 install directory.
        self.main_directory = 'D:/Files/Repositories/rpcs3/bin/'

        # Important subfolders/files, relative to main directory.
        self.exe_path = 'rpcs3.exe'
        self.game_paths = ['dev_hdd0/disc', 'dev_hdd0/game']
        self.user_path = 'dev_hdd0/home/00000001/localusername'

    # Normalizes and joins paths from config.
    def config2path(self, path, *paths):
        return os.path.normpath(os.path.join(path, *paths))