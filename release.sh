#!/usr/bin/env bash

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
# INCLUDING WITHOUT LIMITATION WARRANTIES OF TITLE, MERCHANTABILITY, FITNESS FOR
# A PARTICULAR PURPOSE, NON INFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER
# DEFECTS, ACCURACY, OR THE PRESENT OR ABSENCE OF ERRORS, WHETHER OR NOT
# DISCOVERABLE, ALL TO THE GREATEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW.
#
# For more information, please see
# <http://creativecommons.org/publicdomain/zero/1.0/>

set -e

# Output an error message and exit with status code 1
die() {
    printf '\n\e[31mERROR:\e[m %s\n' "$@" >&2
    exit 1
}

# Log something with a fancy green arrow
log() {
    printf '\n\e[32m=>\e[m %s' "$@"
}

# Print "done" without new line
ok() {
    printf '%s' "done!"
}


printf '\n\e[36m%s\e[m\n' "release.sh has started"

# Get the remote URL of the git repository
GIT_REMOTE_URL="$(git remote get-url --all origin | sed 's/\.git//g')"

# Verify if git is using HTTPS or SSH
if echo "$GIT_REMOTE_URL" | grep -q "https"
then
    GIT_CONNECTION="https"
    GIT_PROJ_INFO=( $(echo "$GIT_REMOTE_URL" | \
        awk -F '/' '{print $4; print $5}') )
else
    GIT_CONNECTION="ssh"
    GIT_PROJ_INFO=( $(echo "$GIT_REMOTE_URL" | \
        awk -F ':' '{print $2}' | \
        awk -F '/' '{print $1; print $2}') )
fi

GIT_USER="${GIT_PROJ_INFO[0]}"
GIT_REPO="${GIT_PROJ_INFO[1]}"
log "using project \"$GIT_REPO\" (on ${GIT_CONNECTION}) of user \"$GIT_USER\""

# <https://github.com/@user/@repo/commit/>
GIT_COMMIT_URL="$(printf "https://github.com/%s/%s/commit/" "$GIT_USER" "$GIT_REPO")"

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
# penultimate tag). Output the content in HTML to a temporary file
log "generating changelog from \"$PENULT_REF\" to \"$LAST_REF\"... "
{
    echo "<h1>Changelog</h1><ul>";
    git log --pretty=oneline "${PENULT_REF}..${LAST_REF}" | \
        awk -v url="$GIT_COMMIT_URL" \
        '{printf "<li><a href=" url $1 "><code>" substr($1, 1, 7) "</code></a>"; $1=""; printf $0; printf "</li>" }';
    echo "</ul>";
} >> /tmp/rcl

# Get the changelog content
CHANGELOG="$(cat /tmp/rcl)"
rm /tmp/rcl
ok

# Make a POST request to GitHub's release API
log "creating release... "
RESPONSE="$(
    curl --user "${GIT_USER}":"${GIT_TOKEN}" \
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
ok

echo "$RESPONSE"
