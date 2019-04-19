#!/usr/bin/env python3

# The person who associated a work with this deed has dedicated the work to the
# public domain by waiving all of his or her rights to the work worldwide under
# copyright law, including all related and neighboring rights, to the extent
# allowed by law.
#
# You can copy, modify, distribute and perform the work, even for commercial
# purposes, all without asking permission.
#
# AFFIRMER OFFERS THE WORK AS-IS AND MAKES NO REPRESENTATIONS OR WARRANTIES OF
# ANY KIND CONCERNING THE WORK, EXPRESS, IMPLIED, STATUTORY OR OTHERWISE,
# INCLUDING WITHOUT LIMITATION WARRANTIES OF TITLE, MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE, NON INFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER
# DEFECTS, ACCURACY, OR THE PRESENT OR ABSENCE OF ERRORS, WHETHER OR NOT
# DISCOVERABLE, ALL TO THE GREATEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW.
#
# For more information, please see
# <http://creativecommons.org/publicdomain/zero/1.0/>

import sys
import unittest
from os.path import dirname
from os.path import abspath

sys.path.append(
    '{}/src'.format(dirname(dirname(abspath(__file__))))
)

from release import exec
from release import git_tag
from release import git_remote
from release import get_remote_data
from release import identify_provider


class ReleasePyTests(unittest.TestCase):
    def test_exec_nonexistent(self):
        self.assertIsNone(exec(['non-existing-cmd']))

    def test_exec_command_right(self):
        self.assertIsNotNone(exec(['pwd']))

    def test_exec_command_wrong(self):
        self.assertIsNotNone(exec(['git', 'stat']))

    def test_git_tag(self):
        self.assertIsNotNone(git_tag())

    def test_git_remote(self):
        self.assertIn('caian-org/release.py', git_remote())

    def test_provider_github(self):
        self.assertEqual(
            identify_provider('https://github.com/caiertl'), 'github')

    def test_provider_gitlab(self):
        self.assertEqual(
            identify_provider('https://gitlab.com/caian.ertl'), 'gitlab')

    def test_provider_unsupported(self):
        self.assertIsNone(
            identify_provider('https://bitbucket.org'))

    def test_remote_https(self):
        err, data = get_remote_data('https://gitlab.com/caian.ertl/project.git')

        x = data['protocol'] == 'https' and \
            data['provider'] == 'gitlab' and \
            data['user'] == 'caian.ertl' and \
            data['repo'] == 'project' and \
            data['commit_url'] == 'https://gitlab.com/caian.ertl/project/commit'

        self.assertTrue(x)

    def test_remote_ssh(self):
        err, data = get_remote_data('git@github.com:caian-org/release.py.git')

        x = data['protocol'] == 'ssh' and \
            data['provider'] == 'github' and \
            data['user'] == 'caian-org' and \
            data['repo'] == 'release.py' and \
            data['commit_url'] == 'https://github.com/caian-org/release.py/commit'

        self.assertTrue(x)


if __name__ == '__main__':
    unittest.main()
