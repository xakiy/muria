"""Config Parser."""

import os
from configparser import ConfigParser, ExtendedInterpolation


class Parser(ConfigParser):
    """Extending ConfigParser with additional getters."""

    def __init__(self, setup, interpolation=ExtendedInterpolation(), **kwargs):
        super(Parser, self).__init__(interpolation=interpolation, **kwargs)
        if os.path.isfile(str(os.environ.get(setup))):
            conf_file = str(os.environ.get(setup))
        else:
            raise EnvironmentError("Env setup belum diatur!")

        if not bool(self.read(conf_file).count(conf_file)):
            raise FileNotFoundError(
                "File konfigurasi %s tidak ditemukan" % setup
            )

        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.set("path", "base_dir", app_path)
        self.set("path", "config_dir", os.path.dirname(os.environ[setup]))

    def getlist(self, section, option, delim=" ", **kwargs):
        return self.get(section, option, **kwargs).split(delim)
