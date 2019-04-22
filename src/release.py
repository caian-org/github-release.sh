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
import json
import base64
from os import environ
from subprocess import Popen
from subprocess import PIPE
from urllib.request import Request
from urllib.request import urlopen


def die(msg):
    print('\033[31mERROR:\033[0m {}'.format(msg))
    sys.exit(1)


def info(msg):
    print('\033[32m=>\033[0m {}'.format(msg))


def exec(c):
    try:
        proc = Popen(c, stdout=PIPE, stderr=PIPE)
    except Exception:
        return True, None

    out, err = proc.communicate()
    if err:
        return True, None

    return None, out.decode('utf-8').rstrip()


def git_remote():
    return exec(['git', 'remote', 'get-url', '--all', 'origin'])


def git_tag():
    return exec(['git', 'tag', '--sort=committerdate'])


def git_log(penult, last):
    return exec(['git', 'log', '--pretty=oneline', '{0}..{1}'.format(
        penult, last
    )])


def identify_provider(prefix):
    if 'github.com' == prefix:
        return 'github'
    elif 'gitlab.com' == prefix:
        return 'gitlab'
    else:
        return None


def generate_changelog(data):
    changelog = ''

    for _ in data['logs']:
        sha = _[:40]
        msg = _[41:]

        changelog += \
            '<li><a href="{0}/{1}"><code>{2}</code></a> {3}</li>'.format(
                data['url'], sha, sha[:7], msg
            )

    return '<h1>Changelog</h1><ul>{0}</ul>'.format(changelog)


def get_remote_data(remote):
    # --------------------------------------------------
    protocol = 'https'

    if 'https://' not in remote:
        protocol = 'ssh'

    # --------------------------------------------------
    commit_url, provider, aux = '', '', ''

    if protocol == 'https':
        aux = remote.split('/')
        provider = identify_provider(aux[2])
    else:
        aux = remote.split(':')
        provider = aux[0].split('@')[1]
        provider = identify_provider(provider)

    if not provider:
        return True, 'unsupported provider'

    # --------------------------------------------------
    auz = remote.split('{}.com'.format(provider))
    auz = auz[1][1:]
    auz = auz[:len(auz) - 4]
    commit_url = 'https://{0}.com/{1}/commit'.format(provider, auz)

    # --------------------------------------------------
    user, repo = '', ''

    if protocol == 'https':
        user = aux[3]
        repo = aux[-1]
    else:
        aux = aux[1].split('/')
        user = aux[0]
        repo = aux[-1]

    repo = repo[:len(repo) - 4]

    return None, {
        'commit_url': commit_url,
        'protocol': protocol,
        'provider': provider,
        'user': user,
        'repo': repo,
    }


def create_release(release):
    url = 'https://api.github.com/repos/{0}/{1}/releases'.format(
        release['git']['user'], release['git']['repo']
    )

    payload = {
        'target_commitish': 'master',
        'tag_name':   release['git']['tags']['last'],
        'name':       release['git']['tags']['last'],
        'body':       release['changelog'],
        'draft':      False,
        'prerelease': False,
    }

    payload = json.dumps(payload).encode('utf-8')

    auth = '{}:{}'.format(release['git']['user'], release['token'])
    auth = base64.b64encode(auth.encode('utf-8'))

    req = Request(url, data=payload)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Basic {}'.format(auth.decode('ascii')))

    res = None
    try:
        res = urlopen(req).read().decode()

    except Exception as e:
        return e.code, None

    return None, res


def main():
    print('\n\033[36m{}\033[0m\n'.format('release.py has started'))

    # --------------------------------------------------
    token = environ.get('RELEASE_AUTH_TOKEN')
    if not token:
        die('token is undefined')

    # --------------------------------------------------
    err, remote = git_remote()
    if err:
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
    err, tags = git_tag()
    if err:
        die('no tags found')

    tags = tags.split('\n')

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

    err, logs = git_log(penult_ref, last_ref)
    if err:
        die('unable to get logs')

    logs = logs.split('\n')
    changelog = generate_changelog({
        'logs': logs,
        'url': data['commit_url'],
    })

    # --------------------------------------------------
    info('creating release...')
    err, res = create_release({
        'git': data,
        'changelog': changelog,
        'token': token,
    })

    if err:
        die('release creation failed with HTTP code "{}"'.format(res))

    print(res)


if __name__ == '__main__':
    main()
