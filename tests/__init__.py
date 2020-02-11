import os

# initialize env testing configurations
try:
    os.environ["MURIA_CONFIG"]
except KeyError:
    os.environ["MURIA_CONFIG"] = os.path.join(
        os.path.dirname(__file__), "settings.ini"
    )
