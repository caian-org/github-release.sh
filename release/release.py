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
from urllib.parse import quote_plus


MOCK_SERVER = 'http://localhost:8080'
TEST_MODE = environ.get('RELEASE_TEST_MODE')


def die(msg):
    print('\033[31mERROR:\033[0m {}'.format(msg))
    sys.exit(1)


def info(msg):
    print('\033[32m=>\033[0m {}'.format(msg))


def do_cmd(cmdl):
    if not isinstance(cmdl, list):
        cmdl = cmdl.split(' ')

    try:
        proc = Popen(cmdl, stdout=PIPE, stderr=PIPE)
    except Exception as err:
        return err, None

    out, err = proc.communicate()
    if err:
        return err, None

    return None, out.decode('utf-8').rstrip()


def git_remote():
    return do_cmd('git remote get-url --all origin')


def git_tag():
    return do_cmd('git tag --sort=committerdate')


def git_log(tags):
    return do_cmd('git log --pretty=online {}..{}'.format(tags['penult'], tags['last']))


def identify_provider(prefix):
    if prefix == 'github.com':
        return 'github'

    if prefix == 'gitlab.com':
        return 'gitlab'

    return None


def generate_changelog(data):
    changelog = ''

    for _ in data['logs']:
        sha = _[:40]
        msg = _[41:]

        changelog += '<li><a href="{0}/{1}"><code>{2}</code></a> {3}</li>'.format(
            data['url'], sha, sha[:7], msg
        )

    return '<h1>Changelog</h1><ul>{0}</ul>'.format(changelog)


def get_remote_data(remote):
    protocol = 'https'

    if 'https://' not in remote:
        protocol = 'ssh'

    aux = ''
    commit_url = ''
    provider = ''

    if protocol == 'https':
        aux = remote.split('/')
        provider = identify_provider(aux[2])
    else:
        aux = remote.split(':')
        provider = aux[0].split('@')[1]
        provider = identify_provider(provider)

    if not provider:
        return True, 'unsupported provider'

    auz = remote.split('{}.com'.format(provider))
    auz = auz[1][1:]
    auz = auz[: len(auz) - 4]
    commit_url = 'https://{0}.com/{1}/commit'.format(provider, auz)

    user = ''
    repo = ''

    if protocol == 'https':
        user = aux[3]
        repo = aux[-1]
    else:
        aux = aux[1].split('/')
        user = aux[0]
        repo = aux[-1]

    repo = repo[: len(repo) - 4]

    return None, {
        'commit_url': commit_url,
        'protocol': protocol,
        'provider': provider,
        'user': user,
        'repo': repo,
    }


def post_request_with_auth(data):
    payload = json.dumps(data['payload']).encode('utf-8')

    key, val = data['auth']

    req = Request(data['url'], data=payload)
    req.add_header('Content-Type', 'application/json')
    req.add_header(key, val)

    res = None
    try:
        res = urlopen(req).read().decode()

    except Exception as e:
        return e.code, None

    return None, res


def create_github_release(data):
    toplevel_domain = TEST_MODE or 'https://api.github.com'

    url = '{0}/repos/{1}/{2}/releases'.format(
        toplevel_domain, data['git']['user'], data['git']['repo']
    )

    payload = {
        'target_commitish': 'master',
        'tag_name': data['git']['tags']['last'],
        'name': data['git']['tags']['last'],
        'body': data['changelog'],
        'draft': False,
        'prerelease': False,
    }

    auth = '{}:{}'.format(data['git']['user'], data['token'])
    auth = base64.b64encode(auth.encode('utf-8'))
    auth = 'Basic {}'.format(auth.decode('ascii'))

    return post_request_with_auth({'url': url, 'payload': payload, 'auth': ('Authorization', auth)})


def create_gitlab_release(data):
    toplevel_domain = 'https://gitlab.com'
    if TEST_MODE:
        toplevel_domain = 'http://localhost:8080'

    proj_path = data['git']['commit_url'].split('https://{}.com/'.format(data['git']['provider']))[1]

    proj_path = proj_path[: len(proj_path) - 7]
    proj_path = quote_plus(proj_path)

    url = '{}/api/v4/projects/{}/releases'.format(toplevel_domain, proj_path)

    payload = ''

    return post_request_with_auth(
        {'url': url, 'pauload': payload, 'auth': ('PRIVATE-TOKEN', data['token'])}
    )


def create_release(data):
    if data['git']['provider'] == 'github':
        return create_github_release(data)

    return create_gitlab_release(data)


def main():
    print('\n\033[36m{}\033[0m\n'.format('release.py has started'))

    token = environ.get('RELEASE_AUTH_TOKEN')
    if not token:
        die('token is undefined')

    err, remote = git_remote()
    if err:
        die('unable to get the remote URL')

    err, data = get_remote_data(remote)
    if err:
        die(data)

    info('detected provider: {}'.format(data['provider']))
    info(
        'performing on project "{0}" (on {1}) of user "{2}"'.format(
            data['repo'], data['protocol'], data['user']
        )
    )

    err, tags = git_tag()
    if err:
        die('no tags found')

    tags = tags.split('\n')

    data['tags'] = {}
    data['tags']['last'] = tags[-1]

    if len(tags) == 1:
        data['tags']['penult'] = 'master'
    else:
        data['tags']['penult'] = tags[-2]

    info(
        'generating changelog from "{0}" to "{1}"...'.format(
            data['tags']['penult'], data['tags']['last']
        )
    )

    err, logs = git_log(data['tags'])
    if err:
        die('unable to get logs')

    logs = logs.split('\n')
    changelog = generate_changelog(
        {
            'logs': logs,
            'url': data['commit_url'],
        }
    )

    info('creating release...')
    err, res = create_release(
        {
            'git': data,
            'changelog': changelog,
            'token': token,
        }
    )

    if err:
        die('release creation failed with HTTP code "{}"'.format(res))

    print(res)


if __name__ == '__main__':
    main()
