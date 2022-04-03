import argparse
import os
import re
import sys

import git

from config_reader import ConfigReader
from utils import Arguments, dir_path, file_path
from version_manager import increase_version, Version


def parse_args() -> Arguments:
    parser = argparse.ArgumentParser(description='EZGit Client.')
    parser.add_argument('-r', '--repo', metavar='repository path', type=dir_path, default='.')
    parser.add_argument('-c', '--config', metavar='configuration file', type=file_path, default='default.yaml')
    parser.add_argument('-p', '--profile', metavar='profile', type=str, default='default')
    parser.add_argument('-f', '--feature-branch', metavar='use feature branch', action=argparse.BooleanOptionalAction)
    parser.add_argument('-i', '--increment-version', metavar='increment version', type=str,
                        choices=[Version.MAJOR.value, Version.MINOR.value, Version.PATCH.value])

    args = parser.parse_args()
    print("Opening Path : %s with config: %s" % (args.repo, args.config))

    return Arguments(config=args.config,
                     repo=args.repo,
                     profile=args.profile,
                     increment_version=args.increment_version,
                     feature_branch=args.feature_branch)


def get_ticket_id(repo_reader: ConfigReader, branch: git.SymbolicReference) -> str:
    m = re.search(repo_reader.repo_config.ticket_structure, str(branch))

    return m.group(1) if m is not None else None


def init_git(git_folder: str, use_feature_branch: bool, repo_reader: ConfigReader):
    g = git.Repo(git_folder)

    remote = next(remote for remote in g.remotes if remote.name == repo_reader.repo_config.remote)
    ticket_id = get_ticket_id(repo_reader, g.active_branch)
    if ticket_id is None:
        sys.exit("You are not inside of a feature branch or your ticket config is invalid!")

    print("Using remote: %s" % remote)
    print("Current Branch: %s, ticket: %s" % (str(g.active_branch), ticket_id))

    for submodule in g.submodules:
        latest_branches = list()
        for remote in submodule.module().remotes:
            # print("Updating submodule %s from remote %s" % (submodule.name, remote.name))
            remote.update()

            # find feature branch with ticket id
            if use_feature_branch:
                for remote_ref in remote.refs:
                    if ticket_id in remote_ref.name:
                        # print("Found ticket in branch; " + remote_ref.name)
                        for commit in submodule.module().iter_commits(rev=remote_ref):
                            if ticket_id in commit.message:
                                latest_branches.append(commit)
                                break
            else:
                raise NotImplementedError("Only feature branches are currently supported!")
        latest_branch = max(latest_branches, key=lambda x: x.committed_date)

        if latest_branch.binsha != submodule.binsha:
            submodule.binsha = latest_branch.binsha
            g.index.add([submodule])
            g.index.commit("%s: update submodule" % ticket_id)
            print("Updating Submodule to SHA: %s" % str(latest_branch))
        else:
            print("Submodule is already up to date!")


if __name__ == '__main__':
    arguments = parse_args()
    reader = ConfigReader(arguments.config, arguments.repo)
    reader.active_config = arguments.profile

    if arguments.increment_version is not None:
        increase_version(Version(arguments.increment_version), reader)

    init_git(arguments.repo, arguments.feature_branch, reader)
