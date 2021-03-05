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

from release.release import do_cmd
from release.release import git_tag
from release.release import git_remote
from release.release import get_remote_data
from release.release import identify_provider
from release.release import generate_changelog


def test_changelog_generation():
    data = {
        'logs': ['16a571c2c43316e332e38b5abcc49490945ec955 feat: initial implementation'],
        'url': 'https://github.com/caian-org/release.py/commit',
    }

    html = '<h1>Changelog</h1><ul><li><a href="https://github.com/caian-org/release.py/commit/16a571c2c43316e332e38b5abcc49490945ec955"><code>16a571c</code></a> feat: initial implementation</li></ul>'

    assert generate_changelog(data) == html

def test_exec_nonexistent():
    err, res = do_cmd(['non-existent-cmd'])

    assert err

def test_exec_command_wrong():
    err, res = do_cmd(['git', 'stat'])

    assert err

def test_exec_command_right():
    err, res = do_cmd(['pwd'])

    assert res is not None

def test_git_tag():
    err, res = git_tag()

    assert res is not None

def test_git_remote():
    err, res = git_remote()

    assert 'caian-org/release.py' in res

def test_provider_github():
    assert identify_provider('github.com') == 'github'

def test_provider_unsupported():
    assert identify_provider('bitbucket.org') is None

def test_remote_https():
    err, data = get_remote_data('https://github.com/caian.ertl/project.git')

    x = (
        data['protocol'] == 'https'
        and data['provider'] == 'github'
        and data['user'] == 'caian.ertl'
        and data['repo'] == 'project'
        and data['commit_url'] == 'https://github.com/caian.ertl/project/commit'
    )

    assert x

def test_remote_ssh():
    err, data = get_remote_data('git@github.com:caian-org/release.py.git')

    x = (
        data['protocol'] == 'ssh'
        and data['provider'] == 'github'
        and data['user'] == 'caian-org'
        and data['repo'] == 'release.py'
        and data['commit_url'] == 'https://github.com/caian-org/release.py/commit'
    )

    assert x

def test_remote_unsupported():
    err, data = get_remote_data('git@bitbycket.org:caian/project.git')

    assert err
