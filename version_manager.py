import enum
import fileinput
import re
import sys

from config_reader import ConfigReader


class Version(enum.Enum):
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'


def increase_version(version_info: Version, repo_reader: ConfigReader):
    with fileinput.input(repo_reader.repo_config.version_config.file, inplace=True) as version_file:
        for line in version_file:
            try:
                m = re.search(repo_reader.repo_config.version_config.version_string_match, line)
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
                    print(line.replace(m.group(0), new_line), end='')
                else:
                    print(line, end='')
            except KeyboardInterrupt:
                sys.exit()
                pass
            except re.error as e:
                print(line, end='')
                print("regex error:", file=sys.stderr)
                print(e, file=sys.stderr)
            except Exception as e:
                print(line, end='')
                print(e, file=sys.stderr)
