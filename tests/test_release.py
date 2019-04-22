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
from release import generate_changelog


class ReleasePyTests(unittest.TestCase):
    def test_changelog_generation(self):
        data = {
            'logs': ['16a571c2c43316e332e38b5abcc49490945ec955 feat: initial implementation'],
            'url':  'https://github.com/caian-org/release.py/commit'
        }

        html = '<h1>Changelog</h1><ul><li><a href="https://github.com/caian-org/release.py/commit/16a571c2c43316e332e38b5abcc49490945ec955"><code>16a571c</code></a> feat: initial implementation</li></ul>'

        self.assertEqual(
            generate_changelog(data), html)

    def test_exec_nonexistent(self):
        err, res = exec(['non-existent-cmd'])

        self.assertTrue(err)

    def test_exec_command_wrong(self):
        err, res = exec(['git', 'stat'])

        self.assertTrue(err)

    def test_exec_command_right(self):
        err, res = exec(['pwd'])

        self.assertIsNotNone(res)

    def test_git_tag(self):
        err, res = git_tag()

        self.assertIsNotNone(res)

    def test_git_remote(self):
        err, res = git_remote()

        self.assertIn('caian-org/release.py', res)

    def test_provider_github(self):
        self.assertEqual(
            identify_provider('github.com'), 'github')

    def test_provider_gitlab(self):
        self.assertEqual(
            identify_provider('gitlab.com'), 'gitlab')

    def test_provider_unsupported(self):
        self.assertIsNone(
            identify_provider('bitbucket.org'))

    def test_remote_https(self):
        err, data = get_remote_data('https://gitlab.com/caian.ertl/project.git')

        x = data['protocol'] == 'https' and \
            data['provider'] == 'gitlab' and \
            data['user'] == 'caian.ertl' and \
            data['repo'] == 'project' and \
            data['commit_url'] == 'https://gitlab.com/caian.ertl/project/commit'

        self.assertTrue(x)

    def test_remote_https_with_namespace(self):
        err, data = get_remote_data('https://gitlab.com/caian-org/internal/sample-apps/ruby/sinatra.git')

        x = data['protocol'] == 'https' and \
            data['provider'] == 'gitlab' and \
            data['user'] == 'caian-org' and \
            data['repo'] == 'sinatra' and \
            data['commit_url'] == 'https://gitlab.com/caian-org/internal/sample-apps/ruby/sinatra/commit'

        self.assertTrue(x)

    def test_remote_ssh(self):
        err, data = get_remote_data('git@github.com:caian-org/release.py.git')

        x = data['protocol'] == 'ssh' and \
            data['provider'] == 'github' and \
            data['user'] == 'caian-org' and \
            data['repo'] == 'release.py' and \
            data['commit_url'] == 'https://github.com/caian-org/release.py/commit'

        self.assertTrue(x)

    def test_remote_ssh_with_namespace(self):
        err, data = get_remote_data('git@gitlab.com:caian.ertl/internal/sample-apps/ruby/sinatra.git')

        x = data['protocol'] == 'ssh' and \
            data['provider'] == 'gitlab' and \
            data['user'] == 'caian.ertl' and \
            data['repo'] == 'sinatra' and \
            data['commit_url'] == 'https://gitlab.com/caian.ertl/internal/sample-apps/ruby/sinatra/commit'

        self.assertTrue(x)

    def test_remote_unsupported(self):
        err, data = get_remote_data('git@bitbycket.org:caian/project.git')

        self.assertTrue(err)


if __name__ == '__main__':
    unittest.main()
