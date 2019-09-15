# GOG Galaxy 2.0 Integration with RPCS3

## Supported Features
* Finds all Disc and PSN games in the RPCS3 directory.
* Launches RPCS3 and loads game.
* Tracks game time.

## Installation

1. Clone or Download this repository to:
* Windows: `%localappdata%\GOG.com\Galaxy\plugins\installed`
* macOS: `~/Library/Application Support/GOG.com/Galaxy/plugins/installed`

2. Rename the folder from "galaxy-integration-rpcs3" to "rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC".

## Configuration

1. Open "config.py" and set the "main_directory" variable to your RPCS3 installation folder. Use single forward slashes only. No other variables need to be modified.

2. Game-specific launch configuration is handled by RPCS3.

