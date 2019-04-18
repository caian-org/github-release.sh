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
from subprocess import Popen
from subprocess import PIPE
from subprocess import DEVNULL
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.request import Request


def die(msg):
    print('\033[31mERROR:\033[0m {}'.format(msg))
    sys.exit(1)


def info(msg):
    print('\033[32m=>\033[0m {}'.format(msg))


def exec(c):
    proc = Popen(c, stdout=PIPE, stderr=DEVNULL)

    out, err = proc.communicate()
    if err:
        return None

    return out.decode('utf-8')


def git_remote():
    return exec(['git', 'remote', 'get-url', '--all', 'origin'])


def git_tags():
    return exec(['git', 'tag', '--sort=committerdate'])


def git_log(penult, last):
    return exec(['git', 'log', '--pretty=oneline', '{0}..{1}'.format(
        penult, last
    )])


def identify_provider(prefix):
    if 'github.com' in prefix:
        return 'github'
    elif 'gitlab.com' in prefix:
        return 'gitlab'
    else:
        return None


def generate_changelog(logs, commit_url):
    changelog = ''

    for L in logs:
        sha = L[:40]
        msg = L[41:]

        changelog += \
            '<li><a href="{0}/{1}"><code>{2}</code></a> {3}</li>'.format(
                commit_url, sha, sha[:7], msg
            )

    return '<h1>Changelog</h1><ul>{0}</ul>'.format(changelog)


def get_remote_data(remote):
    # --------------------------------------------------
    protocol = 'https'
    if 'https://' not in remote:
        protocol = 'ssh'

    # --------------------------------------------------
    commit_url, provider, aux = '', '', ''

    if remote == 'https':
        aux = remote.split('/')
        provider = identify_provider(aux[2])

    else:
        aux = remote.split(':')
        provider = identify_provider(aux[0])

    if not provider:
        return True, 'unsupported provider'

    # --------------------------------------------------
    auz = remote.split('{}.com'.format(provider))
    auz = auz[1][1:]
    auz = auz[:len(auz) - 5]
    commit_url = 'https://{0}.com/{1}/commit'.format(provider, auz)

    # --------------------------------------------------
    user, repo = '', ''

    if remote == 'https':
        user = aux[3]
        repo = aux[-1]
    else:
        aux = aux[1].split('/')
        user = aux[0]
        repo = aux[-1]

    repo = repo.split('.')[0]

    return None, {
        'commit_url': commit_url,
        'protocol': protocol,
        'provider': provider,
        'user': user,
        'repo': repo,
    }


def create_release(data, changelog):
    url = 'https://api.github.com/repos/{0}/{1}/releases'.format(
        data['user'], data['repo']
    )

    payload = {
        'target_commitish': 'master',
        'tag_name':   data['tags']['last'],
        'name':       data['tags']['last'],
        'body':       changelog,
        'draft':      False,
        'prerelease': False,
    }

    req = Request(url, urlencode(payload).encode())
    return urlopen(req).read().decode()


def main():
    print('\n\033[36m{}\033[0m\n'.format('release.py has started'))

    # --------------------------------------------------
    remote = git_remote()

    if not remote:
        die('unable to get the remote URL')

    err, data = get_remote_data(remote)

    if err:
        die(data)

    info('detected provider: {}'.format(data['provider']))
    info('performing on project "{0}" (on {1}) of user "{2}"'.format(
        data['repo'],
        data['protocol'],
        data['user']
    ))

    # --------------------------------------------------
    tags = git_tags().split('\n')
    tags.pop()

    if not tags:
        die('no tags found')

    # --------------------------------------------------
    last_ref, penult_ref = tags[-1], ''

    if len(tags) == 1:
        penult_ref = 'master'
    else:
        penult_ref = tags[-2]

    data['tags'] = {
        'penult': penult_ref,
        'last': last_ref,
    }

    # --------------------------------------------------
    info('generating changelog from "{0}" to "{1}"...'.format(
        penult_ref, last_ref
    ))

    logs = git_log(penult_ref, last_ref).split('\n')
    logs.pop()

    changelog = generate_changelog(logs, data['commit_url'])

    info('creating release...')
    res = create_release(data, changelog)


if __name__ == '__main__':
    main()
