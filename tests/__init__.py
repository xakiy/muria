import os

# initialize default config if not set
try:
    os.environ["MURIA_SETUP"]
except KeyError:
    os.environ["MURIA_SETUP"] = os.path.join(
        os.path.dirname(__file__), "settings.ini"
    )
