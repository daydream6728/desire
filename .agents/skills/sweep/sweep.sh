#!/bin/bash
# Sweep open PRs and issues for USER-authored signal the pipeline hasn't acted
# on: USER comments with no AGENT reply after them, and APPROVE_EMOJI reacts
# from USER on anyone's comment. A turn may not conclude "no unblocked work"
# without a clean sweep — the TODO.md is not a substitute, it is our own state.
#
# GitHub splits comments across two endpoints: `pulls/comments` holds review
# comments attached to a line of the diff (threaded by in_reply_to_id), while
# `issues/comments` holds the conversation tab of issues and PRs alike (flat).
# Both are swept; the endpoint split is what hid a 🚀 for eight hours once.
#
# Reactions listings are one request per flagged comment, so only comments
# carrying the emoji count are queried for who. Unauthenticated GETs work on
# public repos but are rate-limited to 60/hr; GITHUB_TOKEN or GH_TOKEN is used
# when set.
#
# Usage: sweep.sh <owner/repo> [number...]   # default: every open PR and issue
# Exit 0 and silence on a clean sweep, exit 1 with one line per finding.
set -euo pipefail

repo="$1"; shift
python3 - "$repo" "$@" <<'EOF'
import json, os, sys, urllib.request

repo, numbers = sys.argv[1], [int(n) for n in sys.argv[2:]]
USER, AGENT, EMOJI = "toumix", "toumix-agents", "rocket"

def get(path):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{path}"
        + ("&" if "?" in path else "?") + "per_page=100",
        headers={"User-Agent": "sweep", "Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def review_comments(number):  # pulls/ endpoints reject plain issues
    try:
        return get(f"pulls/{number}/comments")
    except urllib.error.HTTPError as error:
        if error.code in (403, 404):
            return []
        raise

if not numbers:
    numbers = sorted({item["number"] for item in get("issues?state=open")})

findings = []
for number in numbers:
    item = get(f"issues/{number}")  # the body carries reactions too, see #48
    if item["reactions"][EMOJI] and any(
            r["user"]["login"] == USER and r["content"] == EMOJI
            for r in get(f"issues/{number}/reactions")):
        findings.append(f"#{number} {EMOJI} from {USER} on the body: "
                        + item["html_url"])
    threads = {}  # review comments threaded by root, conversation flat per number
    comments = [(c, c.get("in_reply_to_id", c["id"]), "pulls")
                for c in review_comments(number)]
    comments += [(c, number, "issues") for c in get(f"issues/{number}/comments")]
    for comment, thread, kind in comments:
        threads.setdefault((kind, thread), []).append(comment)
        if comment["reactions"][EMOJI] and any(
                r["user"]["login"] == USER and r["content"] == EMOJI
                for r in get(f"{kind}/comments/{comment['id']}/reactions")):
            findings.append(f"#{number} {EMOJI} from {USER}: {comment['html_url']}")
    for thread in threads.values():
        answered, asked = False, None
        for comment in thread:  # both endpoints list oldest first
            author = comment["user"]["login"]
            answered = author == AGENT or answered and author != USER
            asked = comment if author == USER else asked
        if asked and not answered:
            findings.append(f"#{number} unanswered {USER} comment: "
                            + asked["html_url"])

print("\n".join(findings) if findings else "clean", file=sys.stderr)
sys.exit(1 if findings else 0)
EOF
