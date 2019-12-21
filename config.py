
import os
import yaml
import logging

class Config:
    def __init__(self):

        # Before anything else, get the user config file and check that its valid.
        base_path = os.path.dirname(os.path.realpath(__file__))
        self.user_config_yml = self.joinpath(base_path, 'user_config.yml')
        self.check_files([self.user_config_yml])

        # Now start getting the user configured values. Normpath main_directory just in case...
        self.main_directory = os.path.normpath(self.get_config_value('main_directory'))
        self.no_gui = self.get_config_value('no_gui')

        # Important files that should be in main_directory.
        self.rpcs3_exe = self.joinpath(self.main_directory, 'rpcs3.exe')
        self.games_yml = self.joinpath(self.main_directory, 'games.yml')
        self.config_yml = self.joinpath(self.main_directory, 'config.yml')

        # Make sure these exist!
        self.check_files([
            self.rpcs3_exe,
            self.games_yml,
            self.config_yml])

        # By default dev_hdd0 is just below main_directory, 
        # but since you can move it anywhere, we need to find it.
        self.dev_hdd0_directory = os.path.normpath(self.find_hdd0())

        # games.yml holds the games you added, 
        # but this is the main game directory (for PSN games, etc).
        self.game_directory = self.joinpath(self.dev_hdd0_directory, 'game')

        # Path to RPCS3's user directory and related files.
        self.user_directory = self.joinpath(self.dev_hdd0_directory, 'home', '00000001')
        self.trophy_directory = self.joinpath(self.user_directory, 'trophy')
        self.localusername = self.joinpath(self.user_directory, 'localusername')

    # Normalizes and joins paths for OS file handling.
    def joinpath(self, path, *paths):
        return os.path.normpath(os.path.join(path, *paths))

    # Grab the user config value for a given key.
    def get_config_value(self, key):
        if os.path.exists(self.user_config_yml):
            with open(self.user_config_yml, 'r') as user_config_file:

                user_config = yaml.load(user_config_file, Loader=yaml.SafeLoader)
                if user_config:
                    try:
                        return user_config[key]
                    except KeyError:
                        logging.error(key + ' value not found in user_config.yml.')
                        raise KeyError()
                else:
                    logging.error('user_config.yml is empty.')
                    raise OSError()
        else:
            logging.error('user_config.yml not found.')
            raise OSError()

    # Find dev_hdd0 from config.yml.
    def find_hdd0(self):
        hdd0 = None
        with open(self.config_yml, 'r') as config_file:

            config = yaml.load(config_file, Loader=yaml.SafeLoader)
            if config:
                try:
                    hdd0 = config['VFS']['/dev_hdd0/']
                except KeyError:
                    logging.error('hdd0 location not found in config.yml.')
                    raise KeyError()
            else:
                logging.error('config.yml is empty.')
                raise OSError()

            # I think it's a safe guess to call this main_directory.
            if '$(EmulatorDir)' in hdd0:
                hdd0 = self.joinpath(
                    self.main_directory, 
                    hdd0.replace('$(EmulatorDir)', ''))

        return hdd0

    # Raises exception if required files have some problem.
    def check_files(self, files):
        should_raise = False

        for file in files:
            filepath = os.path.normpath(file)

            if not os.path.exists(filepath):
                logging.error(filepath + ' not found.')
                should_raise = True

            elif os.stat(filepath).st_size == 0:
                logging.error(filepath + ' is empty.')
                should_raise = True

        # Log all the errors first before blowing up.
        if should_raise:
            raise OSError()
