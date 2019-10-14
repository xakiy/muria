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

        if self.getboolean("security", "secure"):
            priv_key = self.get("security", "private_key")
            pub_key = self.get("security", "public_key")

            if os.path.isfile(priv_key) and os.path.isfile(pub_key):
                priv_key_file = open(priv_key, "r")
                pub_key_file = open(pub_key, "r")
                self.set("security", "private_key", priv_key_file.read())
                self.set("security", "public_key", pub_key_file.read())
                priv_key_file.close()
                pub_key_file.close()
            else:
                raise FileNotFoundError("File SSL tidak ditemukan!")

    def getlist(self, section, option, delim=" ", **kwargs):
        return self.get(section, option, **kwargs).split(delim)

    def getbinary(self, section, option, **kwargs):
        return bytes(self.get(section, option, **kwargs), "utf8")
