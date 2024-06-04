import time
from typing import Any
from os import environ
from decouple import config, RepositoryEnv
from logging import getLogger

START_TIME = time.time()


class ConfigManager:
    def __init__(self) -> None:
        self._env = RepositoryEnv(".env")

    def get(self, name, default=None):
        return self._env.data.get(name) or environ.get(name) or default

    def delete(self, name):
        if name in self._env.data:
            del self._env.data[name]
            self.save()

    def set(self, name, value):
        self._env.data[name] = value
        self.save()

    def keys(self):
        return self._env.data.keys()

    def save(self):
        with open(".env", "w") as file:
            filterVars = list(filter(
                lambda x: x.startswith("VAR_"), self._env.data.keys()
            ))

            for key, value in self._env.data.items():
                
                if key not in filterVars:
                    file.write(f"{key}={value}\n")

            if filterVars:
                file.write("\n# User-System defined Variables\n")

                for key in sorted(filterVars):
                    print(key)
                    file.write(f"{key}={self._env.data[key]}\n")
        return True


Config = ConfigManager()

BOT_NAME = Config.get("NAME") or "Yoru"

LOGS = getLogger(BOT_NAME)
VERSION = "0.0.1"
