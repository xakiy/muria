import os

# initialize default config if not set
try:
    os.environ["MURIA_CONFIG"]
    os.environ["MURIA_MODE"]
except KeyError:
    os.environ["MURIA_CONFIG"] = os.path.join(
        os.path.dirname(__file__), "settings.ini"
    )
    os.environ["MURIA_MODE"] = "TEST"
