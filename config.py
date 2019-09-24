# Make sure to use / instead of \ in file paths.
import os
import yaml

class Config:
    def __init__(self):

        # Point this to the RPCS3 install directory.
        self.main_directory = 'D:/Files/Repositories/rpcs3/bin/'

        # Launch without the main RPCS3 window.
        # Turn this off if launching a game through Galaxy does nothing,
        # as some games don't work without the main window. 
        self.no_gui = True

        # Important files that should be in main_directory.
        self.rpcs3_exe = self.main_directory + 'rpcs3.exe'
        self.games_yml = self.main_directory + 'games.yml'
        self.config_yml = self.main_directory + 'config.yml'

        # By default dev_hdd0 is just below main_directory, 
        # but since you can move it anywhere, we need to find it.
        self.dev_hdd0_directory = self.find_hdd0()

        # games.yml holds the games you added, 
        # but this is the main game directory (for PSN games, etc).
        self.game_directory = self.dev_hdd0_directory + 'game'

        # Path to RPCS3's user directory and related files.
        self.user_directory = self.dev_hdd0_directory + 'home/00000001/'
        self.trophy_directory = self.user_directory + 'trophy/'
        self.localusername = self.user_directory + 'localusername'

    # Normalizes and joins paths for OS file handling.
    def joinpath(self, path, *paths):
        return os.path.normpath(os.path.join(path, *paths))

    # Find dev_hdd0 from config.yml.
    def find_hdd0(self):
        hdd0 = None
        with open(self.config_yml, 'r') as config_file:

            config = yaml.load(config_file, Loader=yaml.SafeLoader)
            hdd0 = config['VFS']['/dev_hdd0/']

            # I think it's a safe guess to call this main_directory.
            if '$(EmulatorDir)' in hdd0:
                hdd0 = hdd0.replace('$(EmulatorDir)', self.main_directory)

        return hdd0