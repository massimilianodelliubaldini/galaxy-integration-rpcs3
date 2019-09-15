import json

__version__ = ''
with open('manifest.json') as manifest:
    man = json.load(manifest)
    __version__ = man['version']
