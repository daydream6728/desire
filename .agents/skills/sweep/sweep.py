#!/usr/bin/env python3
"""Sweep open PRs and issues for USER-authored signal the pipeline hasn't acted
on: threads where USER spoke last, and APPROVE_EMOJI reacts from USER on
anyone's body or comment. A turn may not conclude "no unblocked work" without a
clean sweep — the TODO.md is not a substitute, it is our own state.

A thread is **answered when anyone other than USER has replied since**: the
pipeline does not care which agent closed it. Keying on one AGENT reported 30%
of the review-comment flags on `discopy/discopy` as unanswered when another
agent had already replied and resolved them — all five threads on one PR, every
night for ten nights. A reply whose last line carries the Claude Code
attribution footer counts as an agent's whoever authored it: the adopted PRs
predate the agent handle and were answered from USER's own account, sixteen
threads on one of them.

A finding is marked 👀 when anyone but USER has eye-reacted the comment or body
it points at, which is how a turn tells work in progress from an instruction
that never arrived. No `--since` applies: an old 👀 still says received.

GitHub splits comments across two endpoints: `pulls/comments` holds review
comments attached to a line of the diff (threaded by in_reply_to_id), while
`issues/comments` holds the conversation tab of issues and PRs alike (flat).
Both are swept, and so are the bodies; the endpoint split is what hid a 🚀 for
eight hours once, and body reactions are where two approvals landed the day
this script was written.

`--since` filters on each comment's and reaction's `created_at` so a turn reads
the delta rather than re-triaging the whole pile: a 🚀 has no answered state, so
without it an approval acted on days ago is reported forever. Widen the window
after a turn runs late or dies — a gap is visible and recoverable, which is why
this is an argument and not a file of acknowledged ids we would have to keep
true. MEMORY_REPO's open-PR count is checked whatever the window, since it is an
invariant rather than a delta.

Reactions listings are one request per flagged item, so only bodies and
comments carrying the emoji count are queried for who. Unauthenticated GETs
work on public repos but are rate-limited to 60/hr; GITHUB_TOKEN or GH_TOKEN
is used when set.

Usage: sweep.py [--since <ISO8601>] <owner/repo> [number...]
       # no numbers: every open PR and issue; no --since: everything, ever
Exit 0 and "clean" on a clean sweep, exit 1 with one line per finding.
"""
import json
import os
import sys
import urllib.error
import urllib.request

USER, EMOJI, MEMORY_REPO = "toumix", "rocket", "toumix/memory"
FOOTER = "claude.ai/code"  # the attribution link every agent post signs off with
REACTIONS = {}  # one listing per body or comment, every emoji read off it


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


def reacted(kind, target, emoji, by_user):
    """The reactions of `emoji` on a body or comment, USER's or everyone
    else's. The counts come free with the target, so only the ones carrying the
    emoji cost a request to find out who reacted and when."""
    if not target["reactions"][emoji]:
        return []
    if kind not in REACTIONS:
        REACTIONS[kind] = get(kind)
    return [reaction for reaction in REACTIONS[kind]
            if reaction["content"] == emoji
            and (reaction["user"]["login"] == USER) == by_user]


def approved(kind, target):
    """USER's APPROVE_EMOJI reaction if it is newer than `since`, else None."""
    return next((reaction for reaction in reacted(kind, target, EMOJI, True)
                 if reaction["created_at"] >= since), None)


def seen(kind, target):
    """" 👀" when the pipeline has reacted to say it received the instruction,
    "" when nothing has: a flag alone cannot tell the two apart."""
    return " 👀" if reacted(kind, target, "eyes", False) else ""


def answered(comment):
    """Whether anyone but USER wrote this, the footer deciding for the comments
    an agent posted from USER's account. Bodies are read for that line only."""
    return (comment["user"]["login"] != USER
            or FOOTER in (comment["body"].strip().splitlines() or [""])[-1])


arguments = sys.argv[1:]
since = ""  # ISO 8601 UTC sorts lexicographically, so "" is the epoch
if arguments and arguments[0] == "--since":
    _, since, *arguments = arguments
repo, numbers = arguments[0], [int(n) for n in arguments[1:]]

findings = []
if repo == MEMORY_REPO and not numbers:
    open_prs = get("pulls?state=open")
    print(f"{repo}: {len(open_prs)} open PR(s)"
          + "".join("\n  " + pr["html_url"] for pr in open_prs), file=sys.stderr)
    if len(open_prs) > 1:
        findings.append(
            f"{repo}: {len(open_prs)} open PRs, at most one is allowed — push to"
            " the oldest and close the rest, don't open another")

if not numbers:
    numbers = sorted({item["number"] for item in get("issues?state=open")})
for number in numbers:
    item = get(f"issues/{number}")
    if approved(f"issues/{number}/reactions", item):
        findings.append(f"#{number} {EMOJI} from {USER} on the body: "
                        + item["html_url"] + seen(f"issues/{number}/reactions", item))
    threads = {}  # review comments threaded by root, conversation flat
    comments = [(c, c.get("in_reply_to_id", c["id"]), "pulls")
                for c in review_comments(number)]
    comments += [(c, number, "issues") for c in get(f"issues/{number}/comments")]
    for comment, thread, kind in comments:
        threads.setdefault((kind, thread), []).append(comment)
        reactions = f"{kind}/comments/{comment['id']}/reactions"
        if approved(reactions, comment):
            findings.append(f"#{number} {EMOJI} from {USER}: "
                            + comment["html_url"] + seen(reactions, comment))
    for (kind, _), thread in threads.items():
        asked = thread[-1]  # both endpoints list oldest first
        if not answered(asked) and asked["created_at"] >= since:
            findings.append(
                f"#{number} unanswered {USER} comment: " + asked["html_url"]
                + seen(f"{kind}/comments/{asked['id']}/reactions", asked))

print("\n".join(findings) if findings else "clean", file=sys.stderr)
sys.exit(1 if findings else 0)
