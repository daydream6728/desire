#!/usr/bin/env python3
"""Sweep open PRs and issues for USER signal the pipeline has not acted on:
threads where USER spoke last, APPROVE_EMOJI reacts from USER, the issues closed
inside the window, and MEMORY_REPO's open-PR count. A finding is marked 👀 when
the pipeline has reacted to say it received it. AGENTS.md is the ground truth:
its Config section names USER, the repos and the emoji, and its rules say what
to do with a finding.

Usage: sweep.py [--since <ISO8601 UTC, e.g. 2026-08-18T00:00:00Z>] <owner/repo>
                [number...]
       # no numbers: every open PR and issue; --since windows comments and closes
Exit 0 and "clean" on a clean sweep, exit 1 with one line per finding.
"""
import ast
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

AGENTS = pathlib.Path(__file__).parents[3] / "AGENTS.md"


def config(path):
    """The Config section of AGENTS.md as a dict, so that the pipeline is
    configured in one place and this script hard-codes no repo and no agent."""
    section = path.read_text().split("## Config")[1].split("\n##")[0]
    return {name.strip(): ast.literal_eval(value.strip())
            for line in section.splitlines() if line.startswith("- ")
            for name, _, value in [line[2:].partition("=")] if value}


def get(repo, path):
    """A GitHub REST resource, every page of a listing. A page holds 100 and
    `discopy/discopy` had 153 open items the day this stopped reading one page:
    the tail is the oldest, so a 🚀 on an old issue was invisible for good.
    Unauthenticated GETs work on public repos but are rate-limited to 60/hr;
    GITHUB_TOKEN or GH_TOKEN is used when set."""
    results, page = [], 1
    while True:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/{path}"
            + ("&" if "?" in path else "?") + f"per_page=100&page={page}",
            headers={"User-Agent": "sweep",
                     "Accept": "application/vnd.github+json"})
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(request) as response:
            items = json.load(response)
        if not isinstance(items, list):  # a single issue, comment or user
            return items
        results += items
        if len(items) < 100:
            return results
        page += 1


def review_comments(repo, number):
    """The pulls/ endpoints reject plain issues, which the sweep also covers."""
    try:
        return get(repo, f"pulls/{number}/comments")
    except urllib.error.HTTPError as error:
        if error.code in (403, 404):
            return []
        raise


def reactors(repo, kind, target, emoji, cache):
    """Who reacted with `emoji` on a body or comment, and when. The counts come
    with the target, so only the ones carrying it cost a request, and the
    listing is cached since both emojis are read off the same one."""
    if not target["reactions"][emoji]:
        return []
    if kind not in cache:
        cache[kind] = get(repo, kind)
    return [reaction for reaction in cache[kind] if reaction["content"] == emoji]


def closed_since(repo, since):
    """The issues closed inside the window, with why and by whom. USER answers
    some questions by closing the issue, which leaves no thread to read and no
    open item to walk. One listing per repo, plus one request per issue found
    to say who closed it; without a window there is no delta, hence nothing."""
    for issue in get(repo, f"issues?state=closed&since={since}") if since else []:
        if "pull_request" in issue or issue["closed_at"] < since:
            continue
        closer = get(repo, f"issues/{issue['number']}").get("closed_by") or {}
        reason = f" {issue['state_reason']}" if issue["state_reason"] else ""
        yield (f"#{issue['number']} closed{reason} by "
               f"{closer.get('login', 'unknown')}: " + issue["html_url"])


def approved(repo, kind, target, setup, cache):
    """Whether USER's APPROVE_EMOJI is on the target. No `since`: a react has no
    answered state, so a window hides a live approval as readily as an old one,
    and every approval on a swept target is reported whatever its age."""
    return any(
        reaction["user"]["login"] == setup["USER"]
        for reaction in reactors(
            repo, kind, target, setup["APPROVE_EMOJI"], cache))


def seen(repo, kind, target, setup, cache):
    """" 👀" when the pipeline has reacted to say it received the instruction,
    "" when nothing has: a flag alone cannot tell the two apart. No `since` —
    an old 👀 still says received."""
    return " 👀" if any(
        reaction["user"]["login"] != setup["USER"]
        for reaction in reactors(repo, kind, target, "eyes", cache)) else ""


def answered(comment, setup):
    """Whether anyone but USER wrote this, AGENT_FOOTER deciding for the ones an
    agent posted from USER's account. Bodies are read for that line only."""
    return (comment["user"]["login"] != setup["USER"]
            or setup["AGENT_FOOTER"]
            in (comment["body"].strip().splitlines() or [""])[-1])


def memory(repo, setup):
    """MEMORY_REPO holds one open PR, checked whatever the window since it is an
    invariant rather than a delta."""
    open_prs = get(repo, "pulls?state=open")
    print(f"{repo}: {len(open_prs)} open PR(s)"
          + "".join("\n  " + pr["html_url"] for pr in open_prs), file=sys.stderr)
    return [] if len(open_prs) < 2 else [
        f"{repo}: {len(open_prs)} open PRs, at most one is allowed — push to the"
        " oldest and close the rest, don't open another"]


def item(repo, number, setup, since, cache):
    """The findings on one PR or issue: USER's APPROVE_EMOJI on the body or on
    any comment, and every thread where USER spoke last. GitHub splits comments
    across two endpoints, review comments threaded by in_reply_to_id and the
    conversation tab flat; both are swept, and so are the bodies."""
    findings, threads, body = [], {}, get(repo, f"issues/{number}")
    kind = f"issues/{number}/reactions"
    if approved(repo, kind, body, setup, cache):
        findings.append(
            f"#{number} {setup['APPROVE_EMOJI']} from {setup['USER']} on the"
            f" body: {body['html_url']}" + seen(repo, kind, body, setup, cache))
    comments = [(comment, comment.get("in_reply_to_id", comment["id"]), "pulls")
                for comment in review_comments(repo, number)]
    comments += [(comment, number, "issues")
                 for comment in get(repo, f"issues/{number}/comments")]
    for comment, thread, endpoint in comments:
        threads.setdefault((endpoint, thread), []).append(comment)
        kind = f"{endpoint}/comments/{comment['id']}/reactions"
        if approved(repo, kind, comment, setup, cache):
            findings.append(
                f"#{number} {setup['APPROVE_EMOJI']} from {setup['USER']}:"
                f" {comment['html_url']}"
                + seen(repo, kind, comment, setup, cache))
    for (endpoint, _), thread in threads.items():
        asked = thread[-1]  # both endpoints list oldest first
        kind = f"{endpoint}/comments/{asked['id']}/reactions"
        if not answered(asked, setup) and asked["created_at"] >= since:
            findings.append(
                f"#{number} unanswered {setup['USER']} comment:"
                f" {asked['html_url']}" + seen(repo, kind, asked, setup, cache))
    return findings


def sweep(repo, numbers, since, setup):
    """One line per finding, empty when the sweep is clean."""
    cache, findings = {}, []
    if repo == setup["MEMORY_REPO"] and not numbers:
        findings += memory(repo, setup)
    if not numbers:
        findings += closed_since(repo, since)
        numbers = sorted({
            issue["number"] for issue in get(repo, "issues?state=open")})
    for number in numbers:
        findings += item(repo, number, setup, since, cache)
    return findings


def main(arguments):
    since = ""  # ISO 8601 UTC sorts lexicographically, so "" is the epoch
    if arguments and arguments[0] == "--since":
        _, since, *arguments = arguments
    findings = sweep(arguments[0], [int(n) for n in arguments[1:]], since,
                     config(AGENTS))
    print("\n".join(findings) if findings else "clean", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
