"""Config Parser."""

import os
from configparser import SafeConfigParser, ExtendedInterpolation


class _Configuration(SafeConfigParser):
    """Extending ConfigParser with additional getters."""

    def __init__(self, interpolation=ExtendedInterpolation(), **kwargs):
        super().__init__(interpolation=interpolation, **kwargs)

    def __call__(self, filename, mode):
        config_file = None
        if os.path.isfile(str(os.environ.get(filename))):
            config_file = str(os.environ.get(filename))
        else:
            raise EnvironmentError("Env filename belum diatur!")

        if not bool(self.read(config_file).count(config_file)):
            raise FileNotFoundError(
                "File konfigurasi %s tidak ditemukan" % filename
            )

        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.set("DEFAULT", "app_dir", app_path)
        self.set("DEFAULT", "config_dir", os.path.dirname(config_file))
        self.api_mode = str(os.environ.get("mode", None))
        if self.api_mode not in self:
            self.api_mode = "TEST"
        self.set("DEFAULT", "api_mode", self.api_mode)
        return self[self.api_mode]

    def getlist(self, section, option, delim=" ", **kwargs):
        return self.get(section, option, **kwargs).split(delim)


Configuration = _Configuration()
