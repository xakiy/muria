import os


config_file = os.environ.get("MURIA_SETUP", "")

if config_file is None or config_file is "":
    os.environ["MURIA_SETUP"] = os.path.join(
        os.path.dirname(__file__), "settings.ini"
    )

config_file = os.environ.get("MURIA_SETUP")
