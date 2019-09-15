import json
import sys
import os

def get_version():
    base_path = ''
    version = ''

    if sys.platform in ['win32']:
        base_path = os.path.expandvars('%LocalAppData%')
        
    elif sys.platform in ['darwin']:
        base_path = os.path.join(
            os.path.expanduser('~'), 
            'Library', 
            'Application Support')

    manifest_path = os.path.join(
        base_path,
        'GOG.com',
        'Galaxy',
        'plugins',
        'installed',
        'rpcs3_80F9D16B-5D72-4B95-9D46-2A1EF417C1FC',
        'manifest.json')

    with open(manifest_path) as manifest:
        man = json.load(manifest)
        version = man['version']

    return version
