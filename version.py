import json
import sys
import os

def get_version():
    base_path = ''
    version = ''

    base_path = os.path.dirname(os.path.realpath(__file__))
    manifest_path = os.path.join(base_path, 'manifest.json')

    with open(manifest_path) as manifest:
        man = json.load(manifest)
        version = man['version']

    return version
