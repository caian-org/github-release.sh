# `release.py`

<img src="docs/logo.svg" height="210px" align="right"/>

A KISS solution to easily create project releases.

[![Build Status][travis-shield]][travis-url] [![Code Coverage][codecov-shield]][codecov-url] [![Code Quality][lgtm-shield]][lgtm-url]

- __Minimal.__ No 3rd-party dependency is necessary, only Python 3.x.
- __Simple.__ All required parameters are automagically detected.
- __Language agnostic.__ Create releases for projects written in any language.
- __CI/CD ready.__ Easily integratable in CI/CD pipelines.

[travis-shield]: https://img.shields.io/travis/caian-org/release.py.svg?style=for-the-badge
[travis-url]: https://travis-ci.org/caian-org/release.py

[codecov-shield]: https://img.shields.io/codecov/c/github/caian-org/release.py.svg?style=for-the-badge
[codecov-url]: https://codecov.io/gh/caian-org/release.py

[lgtm-shield]: https://img.shields.io/lgtm/grade/python/g/caian-org/release.py.svg?style=for-the-badge
[lgtm-url]: https://lgtm.com/projects/g/caian-org/release.py/context:python


## Table of Contents

- [How It Works?](#how-it-works)
- [Requirements](#requirements)
- [Usage](#usage)
    - [Attaching Artifacts](#attaching-artifacts)
- [License](#license)
- [Acknowledgements](#acknowledgements)


## How It Works?

`release.py` is a tool that __generates releases on GitHub__. It
should be used in the context of a CI/CD pipeline, at the delivery stage. The
pipeline should be declared in a way that, when a new tag is pushed,
`release.py` is executed after the tests passed, so a new release is
automatically created with the changelog since the last tag.

An example of a Travis-CI pipeline using stages and `release.py`:

```yml
sudo: required
language: node_js

stages:
  - test
  - release

jobs:
  include:
    - stage: test
      name: "Unit tests"
      install:
        - npm install
      script:
        - npm test

    - stage: release
      name: "Create new release"
      script:
        - curl -fsSL https://git.io/fjOZZ | python3
      if: tag IS present
```

The tool lists all the tags for the project and compare the changes from the
last tag to the current one -- If no last tag is detected, it will use the
master branch as the last reference. It then formats the log to an HTML
changelog and posts to the GitHub API. The username, repository name,
connection protocol (HTTPS or SSH) and provider (GitHub or others) detection is
based upon the remote URL of the repository.

Via CLI, one or more artifacts can be attached to the release. A release
message can also be defined (optionally). The API authentication to either
GitHub is made by tokens. The token should be generated for you account and
exposed inside the pipeline via the `RELEASEPY_AUTH_TOKEN` environment
variable.


## Requirements

`release.py` only requires Python 3 (version `3.6` or higher).


## Usage

```sh
curl -fsSL https://git.io/fjOZZ | python3
```


## Attaching Artifacts

*TODO*


## License

To the extent possible under law, [Caian Rais Ertl][me] has waived all
copyright and related or neighboring rights to this work.

[![License][cc-shield]][cc-url]

[me]: https://github.com/caiertl
[cc-shield]: https://forthebadge.com/images/badges/cc-0.svg
[cc-url]: http://creativecommons.org/publicdomain/zero/1.0


## Acknowledgements

`release.py` is highly inspired (by functionality or implementation) on these
projects/scripts:

- [`upload-github-release-asset.sh`][ugra] by [Stefan Buck][stefan]
- [`release`][release] by [Nicolás Sanguinetti][nicolas]
- [`github-release-api`][gra] by [Patrick Durand][patrick]
- [`GoReleaser`][goreleaser] by the [GoReleaser Contributors][contrib]

Icons made by [Icongeek26][icongeek26] from [Flaticon][flaticon] is
licensed by [CC 3.0 BY][cc3].

[ugra]: https://gist.github.com/stefanbuck/ce788fee19ab6eb0b4447a85fc99f447
[release]: https://gist.github.com/foca/38d82e93e32610f5241709f8d5720156
[gra]: https://github.com/pgdurand/github-release-api
[goreleaser]: https://github.com/goreleaser/goreleaser

[stefan]: https://github.com/stefanbuck
[nicolas]: https://github.com/foca
[patrick]: https://github.com/pgdurand
[contrib]: https://github.com/goreleaser/goreleaser/graphs/contributors

[icongeek26]: https://www.flaticon.com/authors/icongeek26
[flaticon]: https://www.flaticon.com
[cc3]: http://creativecommons.org/licenses/by/3.0
