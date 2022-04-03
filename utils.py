import os
from dataclasses import dataclass


@dataclass
class Arguments:
    repo: str
    config: str
    profile: str
    increment_version: str
    feature_branch: bool


def dir_path(string: str) -> str:
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def file_path(string: str) -> str:
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)