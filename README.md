# GOG Galaxy 2.0 Integration with RPCS3

## Supported Features
* Finds all Disc and PSN games known to RPCS3.
* Launches RPCS3 and loads games.
* Tracks game time.
* Imports and tracks trophies/achievements.

## Prerequisites

* [RPCS3 v0.0.7](https://rpcs3.net/) or later

## Installation

### With git (from command line)

- Windows: 
```
cd %localappdata%\GOG.com\Galaxy\plugins\installed
git clone https://github.com/mpm11011/galaxy-integration-rpcs3.git
rename galaxy-integration-rpcs3 rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC
cd rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC
git submodule update --init
```
- macOS: 
```
cd ~/Library/Application Support/GOG.com/Galaxy/plugins/installed
git clone https://github.com/mpm11011/galaxy-integration-rpcs3.git
mv galaxy-integration-rpcs3 rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC
cd rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC
git submodule update --init
```

### Without git

1. Download a zip of this repository this directory and unpack it in:
- Windows: `%localappdata%\GOG.com\Galaxy\plugins\installed`
- macOS: `~/Library/Application Support/GOG.com/Galaxy/plugins/installed`

2. Download a zip of the [devita repository](https://github.com/mpm11011/devita.git) 
and unpack the contents into `galaxy-integration-rpcs3/devita`.

3. Rename the `galaxy-integration-rpcs3` folder to `rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC`.

## Configuration

1. Open `config.py` 

* Set the `main_directory` variable to your RPCS3 installation folder. Use single forward slashes only.

* If some games don't launch from Galaxy, try setting `no_gui` to `False`. Some games don't work yet with no GUI in RPCS3.

2. Add your games in RPCS3 (File > Add Games), so that they can be added to the `games.yml` file. Running a game will also add it to this file.

* This plugin reads from that file, so it is important that your games and their install directories end up here.

* Game-specific launch configuration is handled by RPCS3.

3. (Optional) Open `game_settings.json` (if it does not exist, it will be created after importing games for the first time)

* Each tag you enter should be inside the brackets, surrounded by double quotes, and separated by commas. You can also leave it empty. Here's an example:

```
    "BCUS98137": {
        "name": "MotorStorm™",
        "tags": ["racing", "soundtrack", "destruction"],
        "hidden": false
    },
```

## Acknowledgements

[AHCoder](https://github.com/AHCoder) - Use of the [PS2 Galaxy plugin](https://github.com/AHCoder/galaxy-integration-ps2) as the basis for this plugin.

[GOG](https://github.com/gogcom) - Use of the [Galaxy Plugin API](https://github.com/gogcom/galaxy-integrations-python-api) provided by GOG.

[RPCS3 Team](https://github.com/RPCS3) - For help with interfacing with the RPCS3 system.

[Marshall Ward](https://github.com/marshallward) - Use of the [SFO Python library](https://github.com/marshallward/devita) to open and read PARAM.SFO files.

Thank you!