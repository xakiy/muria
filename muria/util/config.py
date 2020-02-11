"""Config Parser."""

import os
from configparser import SafeConfigParser, ExtendedInterpolation
from urllib.parse import urlparse


class _Configuration(SafeConfigParser):
    """Extending ConfigParser with additional getters."""

    def __init__(self, interpolation=ExtendedInterpolation(), **kwargs):
        super().__init__(interpolation=interpolation, **kwargs)

    def __call__(self, env_ini, env_mode):
        config_file = None
        if os.path.isfile(env_ini):
            config_file = os.path.abspath(env_ini)
        else:
            raise EnvironmentError("Env %s belum diatur!" % env_ini)

        if not bool(self.read(config_file).count(config_file)):
            raise FileNotFoundError(
                "File konfigurasi %s tidak ditemukan" % env_ini
            )

        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.set("DEFAULT", "dir_app", app_path)
        self.set("DEFAULT", "dir_config", os.path.dirname(config_file))

        if env_mode in self:
            self.api_mode = env_mode
        else:
            self.api_mode = 'TEST'

        if self.api_mode == 'DATABASE_URL':
            try:
                url = os.environ[self.api_mode]
            except KeyError:
                raise EnvironmentError("No DATABASE_URL defined!")
            parsed = urlparse(url)
            self.set(self.api_mode, "db_engine", parsed.scheme)
            self.set(self.api_mode, "db_name", os.path.basename(parsed.path))
            user, password = \
                [i.split(':') for i in parsed.netloc.split('@')][0]
            host, port = [i.split(':') for i in parsed.netloc.split('@')][1]
            self.set(self.api_mode, "db_user", user)
            self.set(self.api_mode, "db_password", password)
            self.set(self.api_mode, "db_host", host)
            self.set(self.api_mode, "db_port", port)

        self.set("DEFAULT", "api_mode", self.api_mode)
        return self[self.api_mode]

    def getlist(self, section, option, delim=" ", **kwargs):
        return self.get(section, option, **kwargs).split(delim)


Configuration = _Configuration()
