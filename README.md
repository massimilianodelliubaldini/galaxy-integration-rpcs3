# GOG Galaxy 2.0 Integration with RPCS3

## Supported Features
* Finds all Disc and PSN games in the RPCS3 directory.
* Launches RPCS3 and loads game.
* Tracks game time.

## Installation

1. Clone or Download this repository to:
* Windows: `%localappdata%\GOG.com\Galaxy\plugins\installed`
* macOS: `~/Library/Application Support/GOG.com/Galaxy/plugins/installed`

2. Rename the folder from `galaxy-integration-rpcs3` to `rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC`.

## Configuration

1. Open `config.py` 

* Set the `main_directory` variable to your RPCS3 installation folder. Use single forward slashes only. No other directories need to be modified.

* If some games don't launch from Galaxy, try setting `no_gui` to `False`. Some games don't work yet with no GUI in RPCS3.

2. Game-specific launch configuration is handled by RPCS3.

## Acknowledgements

[AHCoder](https://github.com/AHCoder) - Use of the [PS2 Galaxy plugin](https://github.com/AHCoder/galaxy-integration-ps2) as the basis for this plugin.

[GOG](https://github.com/gogcom) - Use of the [Galaxy Plugin API](https://github.com/gogcom/galaxy-integrations-python-api) provided by GOG.

[Marshall Ward](https://github.com/marshallward) - Use of the [SFO Python library](https://github.com/marshallward/devita) to open and read PARAM.SFO files.