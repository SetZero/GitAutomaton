import unittest
from unittest.mock import patch, mock_open, call
import copy

from ...modules.config_reader import RepoConfig, VersionConfig, CommitMessages
from . import Version, increase_version

read_data = """
    from conans import ConanFile, CMake, tools

class DemoRepo(ConanFile):
    name = "Hello"
    version = "3.3.1"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def source(self):
        self.run("git clone https://github.com/memsharded/hello.git")
        self.run("cd hello && git checkout static_shared")
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("hello/CMakeLists.txt", "PROJECT(MyHello)", '''PROJECT(MyHello)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="hello")
        cmake.build()

        # Explicit way:
        # self.run('cmake "%s/hello" %s' % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="hello")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]
"""


class TestVersionIncrement(unittest.TestCase):
    """
    Tests version upgrades
    """

    def setUp(self):
        version_config = VersionConfig(version_string_match=r'version = \"(\d+\.\d+\.\d+)+\"', file="/home/someuser")
        commit_messages = CommitMessages(update_submodule="{ticket_id}: commit message")

        self.repo_config = RepoConfig(remote="test",
                                      ticket_structure="test",
                                      default_branch="test",
                                      version_config=version_config,
                                      commit_messages=commit_messages)

        self.invalid_repo_config = copy.deepcopy(self.repo_config)
        self.invalid_repo_config.version_config = VersionConfig(version_string_match=r'(test', file="/home/someuser")

    @patch("builtins.open", new_callable=mock_open, read_data=read_data)
    def test_major(self, mock_file):
        increase_version(Version.MAJOR, self.repo_config)

        handle = self.setup_file(mock_file)
        handle.write.assert_has_calls([call('    version = "4.3.1"\n')])

    @patch("builtins.open", new_callable=mock_open, read_data=read_data)
    def test_minor(self, mock_file):
        increase_version(Version.MINOR, self.repo_config)

        handle = self.setup_file(mock_file)
        handle.write.assert_has_calls([call('    version = "3.4.1"\n')])

    @patch("builtins.open", new_callable=mock_open, read_data=read_data)
    def test_patch(self, mock_file):
        increase_version(Version.PATCH, self.repo_config)
        handle = self.setup_file(mock_file)
        handle.write.assert_has_calls([call('    version = "3.3.2"\n')])

    @patch("builtins.open", new_callable=mock_open, read_data=read_data)
    def test_invalid_regex(self, mock_file):
        from io import StringIO

        out = StringIO()
        increase_version(Version.PATCH, self.invalid_repo_config, log=out)
        output = out.getvalue().strip()

        assert "regex error:" in output

    @patch("builtins.open", new_callable=mock_open, read_data=read_data)
    def test_invalid_file(self, mock_file):
        from io import StringIO
        mock_file.side_effect = IOError

        out = StringIO()
        increase_version(Version.PATCH, self.invalid_repo_config, log=out)
        output = out.getvalue().strip()

        assert "error writing file:" in output

    def setup_file(self, mock_file):
        calls = [call(self.repo_config.version_config.file, 'r'),
                 call(self.repo_config.version_config.file, 'w')]
        mock_file.assert_has_calls(calls, any_order=True)
        handle = mock_file()
        self.assertEqual(handle.write.call_count, 39)
        return handle


if __name__ == '__main__':
    unittest.main()
