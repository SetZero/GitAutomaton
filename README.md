# EzGit Client

EzGit is a utility client which allows you to automate certain common git tasks.

## Automate Tasks

EzGit enables to automation of the following common tasks:
- Version increment
- Update Submodule to the latest version of a Ticket

## Supports Multiple Profiles

EzGit allows the usage of multiple profiles, which can be especially useful if you are working on multiple projects

## Usage

EzGit uses a config file and command line parameters for configuration.

### Config

```yaml
# list of all available profiles
config:
  # profile with name 'default'
  default:
    remote: local                                             # name of remote repository
    ticket_structure: "mybla#([0-9]+)"                        # regex used for tickets inside of branches/commits
    versioning:                                               # versioning information
      file: "conanfile.py"                                    # file containing version information, currently only one supported
      version_string_match: 'version = \"(\d+\.\d+\.\d+)+\"'  # regex to use for version changing

```
| Key                             | Description                                                                                                                                                           |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| remote                          | Name of the remote branch which should be used for information gathering of most current git changes                                                                  |
| ticket structure                | Ticket structure is used to identify ticket information inside of your commits / branches, e.g. branch `mybla#1-test-branch` or commit `mybla#1: chaned testing data` |
| versioning/file                 | File used for versioning information. This file will contain a version string which will be updated                                                                   |
| versioning/version_string_match | Regex to match the version information. The regex must match a version string seperated by a ".". The maximum depth is 3. Examples are `42`, `7.77`, `47.1.1`         |

### Command Line Parameters

| Parameter               | Description                                                               |
|-------------------------|---------------------------------------------------------------------------|
| -h                      | Show help                                                                 |
| -r, --repo              | specify repository which will be used, e.g. `/home/repos/example-project` |
| -c, --config            | specify config location (see [Config](#Config)), e.g. `./my-config.yaml`  |
| -p, --profile           | Profile from config which you want to use, e.g. `default`                 |
| -i, --increment-version | Increment version, possible values: `major`, `patch`, `minor`             |


**Example Usage**
```console
python3 ezgit.py --repo ./demo_repo --config config/local.yaml --profile default -i major
```