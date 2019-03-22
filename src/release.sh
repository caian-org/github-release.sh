#!/usr/bin/env bash

set -e

die() {
    printf '\n\e[31mERROR:\e[m %s\n' "$@" >&2
    exit 1
}

puts() {
    printf "%s" $@
}

# Get the remote URL of the git repository
GIT_REMOTE_URL="$(git remote get-url --all origin | sed 's/\.git//g')"

# Made an array out of the user and repository name
GIT_PROJ_INFO=( $(echo $GIT_REMOTE_URL | awk -F '/' '{print $4; print $5}') )
GIT_USER="${GIT_PROJ_INFO[0]}"
GIT_REPO="${GIT_PROJ_INFO[1]}"

# <github.com/@user/@repo/commit/>
GIT_COMMIT_URL="$(printf "%s/commit/" $GIT_REMOTE_URL)"

# Get the tags in chronological order (oldest to newest)
GIT_TAGS="$(git tag --sort=committerdate | tail -n 2)"

# Fail if there is no tags
if [ -z "$GIT_TAGS" ]
then
    die "no tags found"
fi

# Count how many tags there are
GIT_TAGS_COUNT="$(echo "$GIT_TAGS" | cat -n | wc -l)"

# If there's only one tag, use the master branch as the last reference
# Otherwise, use the penultimate tag
if [ "$GIT_TAGS_COUNT" -eq 1 ]
then
    PENULT_REF="master"
else
    PENULT_REF="$(echo "$GIT_TAGS" | head -n 1)"
fi

LAST_REF="$(echo "$GIT_TAGS" | tail -n 1)"

# Compare the last tag against the last reference (the master branch or the
# penultimate tag). Output in HTML.
echo "<h1>Changelog</h1><ul>" >> /tmp/rcl
git log --pretty=oneline "${PENULT_REF}..${LAST_REF}" | \
    awk -v url="$GIT_COMMIT_URL" \
    '{printf "<li><a href=" url $1 "><code>" substr($1, 1, 7) "</code></a>"; $1=""; printf $0; printf "</li>" }' \
    >> /tmp/rcl
echo "</ul>" >> /tmp/rcl

CHANGELOG="$(cat /tmp/rcl)"
rm /tmp/rcl

RESPONSE="$(
    curl --user ${GIT_USER}:${GIT_TOKEN} \
         --request POST \
         --fail \
         --silent \
         --location \
         --data @- \
         "https://api.github.com/repos/${GIT_USER}/${GIT_REPO}/releases" <<END
         {
            "tag_name": "$LAST_REF",
            "target_commitish": "master",
            "name": "$LAST_REF",
            "body": "$CHANGELOG",
            "draft": false,
            "prerelease": false
         }
END
)"

echo "$RESPONSE"
