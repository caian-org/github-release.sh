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


## About

`release.py` is a tool that generates releases on GitHub and GitLab (WIP). It
should be used in the context of a CI/CD pipeline, at the delivery stage. The
pipeline should be declared in a way that, when a new tag is pushed,
`release.py` is executed after the tests passed, so a new release is
automatically created with the changelog since the last tag.

The tool lists all the tags for the project and compare the changes from the
last tag to the current one. It then formats the log to an HTML changelog and
posts to the GitHub/GitLab API. The username, repository name, connection
protocol (HTTPS or SSH) and provider (GitHub or Gitlab) detection is based upon
the remote URL. Via CLI, one or more artifacts can be uploaded. A release
message can also be defined -- though completely optional.

The API authentication to either GitHub ou GitLab is made by tokens. The token
should be generated for you account and exposed inside the pipeline via the
`RELEASEPY_AUTH_TOKEN` environment variable.


## Usage

```sh
curl -fsSL https://git.io/fjOZZ | python
```


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
