import enum
import fileinput
import re
import sys

from src.modules.config_reader import RepoConfig


class Version(enum.Enum):
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'


def increase_version(version_info: Version, repo_reader: RepoConfig, log=sys.stdout):
    lines = None
    try:
        with open(repo_reader.version_config.file, 'r') as f:
            lines = f.readlines()

        with open(repo_reader.version_config.file, 'w') as wline:
            for line in lines:
                m = re.search(repo_reader.version_config.version_string_match, line)
                if m is not None:
                    major, minor, patch = (list(map(lambda x: int(x), str(m.group(1)).split('.'))) + [None] * 3)[:3]
                    if version_info == Version.MAJOR:
                        major += 1
                    elif version_info == Version.MINOR:
                        minor += 1
                    elif version_info == Version.PATCH:
                        patch += 1
                    new_version = '.'.join(map(lambda x: str(x), [x for x in [major, minor, patch] if x is not None]))
                    new_line = m.group(0).replace(m.group(1), new_version)
                    wline.write(line.replace(m.group(0), new_line))
                else:
                    wline.write(line)
    except re.error as e:
        _reset_file(lines, repo_reader)
        log.write("regex error: {}".format(e))
    except EnvironmentError as e:
        _reset_file(lines, repo_reader)
        log.write("error writing file: {}".format(e))


def _reset_file(lines, repo_reader):
    if lines is None:
        return

    with open(repo_reader.version_config.file, 'w') as f:
        for line in lines:
            f.write(line)
