"""Config Parser."""

import os
from configparser import SafeConfigParser, ExtendedInterpolation
from urllib.parse import urlparse
from pathlib import Path


class _Configuration(SafeConfigParser):
    """
    ConfigParser with Additional Getter Types.

    When called it will search for env variables,
    env_ini that points to the config file, and env_mode that
    coresponds with section within that config file.

    """

    def __init__(self, interpolation=ExtendedInterpolation(), **kwargs):
        super().__init__(interpolation=interpolation, **kwargs)

    def __call__(self, env_ini, env_mode):
        """
        Main call method.

        Parameters
        ----------
        env_ini : str
            Path to config file
        env_mode : str, optional
            A section selector within the config file

        Returns
        -------
        object
            configuration object of env_mode section
        """
        config_file = Path(env_ini)

        if not config_file.is_file():
            raise FileNotFoundError(
                "File konfigurasi %s tidak ditemukan" % env_ini
            )
        # DEPRECATED:
        # python 3.5 'open' limitation to handle path like object
        if not bool(self.read(str(config_file)).count(env_ini)):
            raise IOError("File konfigurasi %s tak terbaca!" % env_ini)

        dir_app = Path(__file__).parent.parent

        # Muria absolute directory
        self.set("DEFAULT", "dir_app", str(dir_app))

        # Muria test directory
        self.set("DEFAULT", "dir_test", str(Path(dir_app.parent, "tests")))

        # points to working directory where Muria is invoked
        self.set("DEFAULT", "dir_ref", str(Path.cwd()))

        if env_mode in self:
            self.api_mode = env_mode
        else:
            self.api_mode = 'TEST'

        self._heroku_parse()

        self._directory_init()

        self.set("DEFAULT", "api_mode", self.api_mode)
        return self[self.api_mode]

    def _heroku_parse(self):
        # Heroku DATABASE_URL env extractor
        if self.api_mode == 'DATABASE_URL':
            try:
                # first try to use available env config
                url = os.environ[self.api_mode]
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
            except KeyError:
                # fallback to config values
                pass

    def _directory_init(self):
        # Directories initialization
        # NOTE: 0o004 or world readable is only make sense if you serve file directly to
        # the world.
        # So does these folders need no executable bit set.
        permissions = {
            "dir_doc": 0o766,
            "dir_image": 0o766,
            "dir_temp": 0o766
        }
        # set to 0o750 for server need to execute the script
        default_mode = 0o750
        dirs = [k for k in self[self.api_mode].keys() if k.startswith('dir_')]
        for path in dirs:
            if path not in ('dir_app'):
                directory = self.get(self.api_mode, path)
                folder = Path(directory)
                folder.mkdir(parents=True, exist_ok=True)
                folder.chmod(permissions.get(path, default_mode))

    def getlist(self, section, option, delim=" ", **kwargs):
        """Return value as a list."""
        return self.get(section, option, **kwargs).split(delim)


Configuration = _Configuration()
