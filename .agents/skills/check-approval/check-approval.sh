#!/bin/bash
# Check whether USER reacted to a comment with APPROVE_EMOJI.
#
# No GitHub MCP tool returns who reacted, and a plain WebFetch against the
# REST API 403s (GitHub rejects requests with no User-Agent). This shells out
# to curl instead: reactions on public repos are unauthenticated GETs.
#
# GitHub splits comments across two endpoints and a comment id alone does not
# say which it is: `pulls/comments` holds review comments, i.e. the ones
# attached to a line of the diff, while `issues/comments` holds every comment
# in the conversation tab of an issue OR a pull request. Both are queried,
# since a 🚀 on a plain PR comment is invisible to the first one.
#
# Usage: check-approval.sh <owner/repo> <comment-id> [user] [emoji]
set -euo pipefail

repo="$1" id="$2" user="${3:-toumix}" emoji="${4:-rocket}"

for kind in pulls issues; do
  if curl -sS -H "User-Agent: curl" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$repo/$kind/comments/$id/reactions" \
    | python3 -c "
import json, sys
reactions = json.load(sys.stdin)
sys.exit(0 if isinstance(reactions, list) and any(
    r['user']['login'] == '$user' and r['content'] == '$emoji'
    for r in reactions) else 1)
"; then
    echo approved
    exit 0
  fi
done

echo "not approved"
exit 1
