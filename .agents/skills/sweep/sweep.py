#!/usr/bin/env python3
"""Sweep open PRs and issues for USER-authored signal the pipeline hasn't acted
on: USER comments with no AGENT reply after them, and APPROVE_EMOJI reacts from
USER on anyone's body or comment. A turn may not conclude "no unblocked work"
without a clean sweep — the TODO.md is not a substitute, it is our own state.

GitHub splits comments across two endpoints: `pulls/comments` holds review
comments attached to a line of the diff (threaded by in_reply_to_id), while
`issues/comments` holds the conversation tab of issues and PRs alike (flat).
Both are swept, and so are the bodies; the endpoint split is what hid a 🚀 for
eight hours once, and body reactions are where two approvals landed the day
this script was written.

Reactions listings are one request per flagged item, so only bodies and
comments carrying the emoji count are queried for who. Unauthenticated GETs
work on public repos but are rate-limited to 60/hr; GITHUB_TOKEN or GH_TOKEN
is used when set.

Usage: sweep.py <owner/repo> [number...]   # default: every open PR and issue
Exit 0 and "clean" on a clean sweep, exit 1 with one line per finding.
"""
import json
import os
import sys
import urllib.error
import urllib.request

USER, AGENT, EMOJI = "toumix", "toumix-agents", "rocket"


def get(path):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{path}"
        + ("&" if "?" in path else "?") + "per_page=100",
        headers={"User-Agent": "sweep", "Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def review_comments(number):
    """The pulls/ endpoints reject plain issues, which the sweep also covers."""
    try:
        return get(f"pulls/{number}/comments")
    except urllib.error.HTTPError as error:
        if error.code in (403, 404):
            return []
        raise


def approved(kind, target):
    """Whether USER reacted with APPROVE_EMOJI, counts first to save requests."""
    return target["reactions"][EMOJI] and any(
        reaction["user"]["login"] == USER and reaction["content"] == EMOJI
        for reaction in get(kind))


repo, numbers = sys.argv[1], [int(n) for n in sys.argv[2:]]
if not numbers:
    numbers = sorted({item["number"] for item in get("issues?state=open")})

findings = []
for number in numbers:
    item = get(f"issues/{number}")
    if approved(f"issues/{number}/reactions", item):
        findings.append(
            f"#{number} {EMOJI} from {USER} on the body: " + item["html_url"])
    threads = {}  # review comments threaded by root, conversation flat
    comments = [(c, c.get("in_reply_to_id", c["id"]), "pulls")
                for c in review_comments(number)]
    comments += [(c, number, "issues") for c in get(f"issues/{number}/comments")]
    for comment, thread, kind in comments:
        threads.setdefault((kind, thread), []).append(comment)
        if approved(f"{kind}/comments/{comment['id']}/reactions", comment):
            findings.append(
                f"#{number} {EMOJI} from {USER}: " + comment["html_url"])
    for thread in threads.values():
        answered, asked = False, None
        for comment in thread:  # both endpoints list oldest first
            author = comment["user"]["login"]
            answered = author == AGENT or answered and author != USER
            asked = comment if author == USER else asked
        if asked and not answered:
            findings.append(
                f"#{number} unanswered {USER} comment: " + asked["html_url"])

print("\n".join(findings) if findings else "clean", file=sys.stderr)
sys.exit(1 if findings else 0)
