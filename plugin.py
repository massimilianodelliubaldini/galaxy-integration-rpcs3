import sys
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform

class RPCS3Plugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.Generic, # PS3 is not a supported platform yet.
            "0.1", # Version
            reader,
            writer,
            token
        )

    # implement methods
    async def authenticate(self, stored_credentials=None):
        pass

def main():
    create_and_run_plugin(RPCS3Plugin, sys.argv)

# run plugin event loop
if __name__ == "__main__":
    main()
