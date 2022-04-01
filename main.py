import argparse
import os
import re
import sys
from dataclasses import dataclass

import git

from config_reader import ConfigReader


@dataclass
class Arguments:
    folder: str
    config: str
    profile: str
    increase_version: str


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)


def parse_args() -> Arguments:
    parser = argparse.ArgumentParser(description='EZGit Client.')
    parser.add_argument('-f', '--folder', metavar='f', type=dir_path, default='.')
    parser.add_argument('-c', '--config', metavar='c', type=file_path, default='default.yaml')
    parser.add_argument('-p', '--profile', metavar='p', type=str, default='default')
    parser.add_argument('-i', '--increase-version', metavar='i', type=str, choices=['major', 'minor', 'patch'])

    args = parser.parse_args()
    print("Opening Path : %s with config: %s" % (args.folder, args.config))

    return Arguments(config=args.config,
                     folder=args.folder,
                     profile=args.profile,
                     increase_version=args.increase_version)


def get_ticket_id(repo_reader: ConfigReader, branch: git.SymbolicReference) -> str:
    m = re.search(repo_reader.repo_config.ticket_structure, str(branch))

    return m.group(1) if m is not None else None


def init_submodules(git_folder: str, repo_reader: ConfigReader):
    g = git.Repo(git_folder)

    remote = next(remote for remote in g.remotes if remote.name == repo_reader.repo_config.remote)
    ticket_id = get_ticket_id(repo_reader, g.active_branch)
    print(g.active_branch)
    if ticket_id is None:
        sys.exit("You are not inside of a feature branch or your ticket config is invalid!")

    print("Using remote: %s" % remote)
    print("Current Branch: %s, ticket: %s" % (str(g.active_branch), ticket_id))


if __name__ == '__main__':
    arguments = parse_args()
    reader = ConfigReader(arguments.config)
    reader.active_config = arguments.profile
    init_submodules(arguments.folder, reader)
