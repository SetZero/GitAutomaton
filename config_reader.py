import pathlib
import typing
from dataclasses import dataclass

import yaml


@dataclass
class VersionConfig:
    version_string_match: str
    file: typing.Union[str, pathlib.Path]


@dataclass
class RepoConfig:
    remote: str
    ticket_structure: str
    version_config: VersionConfig


class ConfigReader:
    def __init__(self, config_path: str, repo_path: str, active_config=None):
        self._active_config = active_config
        self.__repo_path = repo_path

        self.__read_config(config_path)

    def __read_config(self, config_path: str):
        with open(config_path, "r") as stream:
            try:
                self._data = yaml.safe_load(stream)
                if self.active_config is not None:
                    self.__create_repo_config()
            except yaml.YAMLError as exc:
                print(exc)

    def __create_repo_config(self):
        version_file_path = pathlib.Path(self.__repo_path).joinpath(
            self._data['config'][self.active_config]['versioning']['file'])
        version_info = VersionConfig(file=version_file_path,
                                     version_string_match=self._data['config'][self.active_config]['versioning'][
                                         'version_string_match'])

        self._repo_data = RepoConfig(remote=self._data['config'][self.active_config]['remote'],
                                     ticket_structure=self._data['config'][self.active_config]['ticket_structure'],
                                     version_config=version_info)

    @property
    def repo_config(self):
        assert self.active_config is not None

        return self._repo_data

    @property
    def active_config(self):
        return self._active_config

    @active_config.setter
    def active_config(self, value: str):
        self._active_config = value
        self.__create_repo_config()

    @active_config.deleter
    def active_config(self):
        del self._active_config
