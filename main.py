import argparse
import os
import re
import sys

import git

from config_reader import ConfigReader


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


def parse_args():
    parser = argparse.ArgumentParser(description='EZGit Client.')
    parser.add_argument('--folder', metavar='f', type=dir_path, default='.')
    parser.add_argument('--config', metavar='c', type=file_path, default='default.yaml')
    parser.add_argument('--profile', metavar='p', type=str, default='default')

    args = parser.parse_args()
    print("Opening Path : %s with config: %s" % (args.folder, args.config))
    return args.config, args.folder, args.profile


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
    config, folder, profile = parse_args()
    reader = ConfigReader(config)
    reader.active_config = profile
    init_submodules(folder, reader)
