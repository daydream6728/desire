#!/usr/bin/env python3
"""Sweep open PRs and issues for USER signal the pipeline has not acted on:
bodies and threads where USER spoke last, APPROVE_EMOJI reacts from USER, the
issues closed inside the window, MEMORY_REPO's open-PR count and the state of
each AGENT-owned `TODO.md`. A finding is marked 👀 when the pipeline has reacted
to say it received it. config.env is the ground truth for USER, the repos
and the emoji; AGENTS.md's rules say what to do with a finding.

Usage: sweep.py [--since <ISO8601 UTC, e.g. 2026-08-18T00:00:00Z>] <owner/repo>
                [number...]
       # no numbers: every open PR and issue; --since windows the closes only
Exit 0 and "clean" on a clean sweep, exit 1 with one line per finding. Open
`TODO.md` boxes are printed as context and do not make the sweep dirty.
"""
import base64
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

CONFIG = pathlib.Path(__file__).parents[3] / "config.env"
BOX = re.compile(r"^\s*[-*] \[([^]]*)\]")
CLAIM = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?"
                   r"(?:Z|[+-]\d{2}:?\d{2})?)?")
STALE = datetime.timedelta(hours=12)


def config(path):
    """config.env as a dict, so that the pipeline is configured in one place
    and this script hard-codes no repo and no agent. A value is everything
    after the first `=`; WORK_REPOS is a comma-separated list and ADOPTED_PRS
    space-separated `repo:number,number` entries. A line carrying no `=`
    raises rather than parsing to a key nothing will look up, and a key the
    file does not set is absent, so a caller reading it raises too."""
    setup = {}
    for line in path.read_text().splitlines():
        key, separator, value = line.partition("=")
        if line.strip() and (not separator or not key.strip()):
            raise ValueError(f"config.env: no key in {line!r}")
        if line.strip():
            setup[key.strip()] = value.strip()
    if "WORK_REPOS" in setup:
        setup["WORK_REPOS"] = setup["WORK_REPOS"].split(",")
    if "ADOPTED_PRS" in setup:
        setup["ADOPTED_PRS"] = {
            repo: [int(number) for number in numbers.split(",") if number]
            for entry in setup["ADOPTED_PRS"].split()
            for repo, _, numbers in [entry.partition(":")]}
    return setup


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
    open item to walk. One listing per repo, which carries the closer as well
    as the reason; without a window there is no delta, hence nothing."""
    for issue in get(repo, f"issues?state=closed&since={since}") if since else []:
        if "pull_request" in issue or issue["closed_at"] < since:
            continue
        closer = issue.get("closed_by") or {}
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
    agent posted from USER's account. Bodies are read for that line only, and
    an issue opened with no description has `None` for one."""
    return (comment["user"]["login"] != setup["USER"]
            or setup["AGENT_FOOTER"]
            in ((comment["body"] or "").strip().splitlines() or [""])[-1])


def memory(repo, setup):
    """MEMORY_REPO holds one open PR, checked whatever the window since it is an
    invariant rather than a delta."""
    open_prs = get(repo, "pulls?state=open")
    print(f"{repo}: {len(open_prs)} open PR(s)"
          + "".join("\n  " + pr["html_url"] for pr in open_prs), file=sys.stderr)
    return [] if len(open_prs) < 2 else [
        f"{repo}: {len(open_prs)} open PRs, at most one is allowed — push to the"
        " oldest and close the rest, don't open another"]


def heads(repo, cache):
    """Every open pull request by number. `TODO.md` is read off the head
    commit, which the listing already carries, so the whole repo costs one
    request rather than one per pull request."""
    if "heads" not in cache:
        cache["heads"] = {pull["number"]: pull
                          for pull in get(repo, "pulls?state=open")}
    return cache["heads"]


def contents(repo, path, ref):
    """A file at one commit, `None` when that commit does not carry it: a
    missing `TODO.md` is a finding here rather than an error. Undecodable bytes
    are replaced rather than raised, since one unreadable file would otherwise
    abort the whole sweep. `validate=True` is wrong here — GitHub wraps the
    base64 it serves, which the strict decoder rejects."""
    try:
        blob = get(repo, f"contents/{path}?ref={ref}")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    return base64.b64decode(blob["content"]).decode(errors="replace")


def claimed(box):
    """When a `[WIP]` box was claimed, `None` when it carries no readable date.
    Rule 3 stamps `@<SessionID>-<yyyy-MM-dd HH:mm>`, in practice with an offset
    or a `Z` and sometimes a range, so the first date on the line wins and a
    naive one is read as UTC."""
    stamp = CLAIM.search(box)
    if not stamp:
        return None
    text = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2",
                  stamp.group().replace(" ", "T").replace("Z", "+00:00"))
    try:
        when = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    return when if when.tzinfo else when.replace(
        tzinfo=datetime.timezone.utc)


def cleared(repo, head, cache):
    """Whether this branch carried a `TODO.md` and deleted it, which is what
    clears the merge gate. Both cases read as missing at the head, and the
    diff cannot tell them apart either: adding a file and deleting it again
    nets out to nothing. The branch's own commits touching the path do, once
    the ones it inherits from `main` are taken out. Asked only of a branch
    already known to have no `TODO.md`."""
    if "cleared" not in cache:
        cache["cleared"] = {commit["sha"] for commit in get(
            repo, "commits?sha=main&path=TODO.md")}
    return any(commit["sha"] not in cache["cleared"] for commit in get(
        repo, f"commits?sha={head}&path=TODO.md"))


def elapsed(age):
    """An age in whole hours, in days once there are two of them: the window
    is twelve hours and the claims that break it run to weeks."""
    hours = int(age.total_seconds() // 3600)
    return f"{hours // 24} days" if hours >= 48 else f"{hours} hours"


def owned(repo, number, body, setup):
    """Whether the pipeline is answerable for this pull request: AGENT opened
    it or ADOPTED_PRS lists it, the same test the board and the scans use.
    Nobody else's branch owes us a `TODO.md`, and neither does one in
    DESIRE_REPO or MEMORY_REPO — the rule binds where the work happens."""
    return "pull_request" in body and repo in setup["WORK_REPOS"] and (
        body["user"]["login"] == setup["AGENT"]
        or number in setup.get("ADOPTED_PRS", {}).get(repo, []))


def todo(repo, number, body, setup, cache):
    """The `TODO.md` findings on one AGENT-owned pull request. Its boxes are
    the mutex between parallel agents and deleting the file is what clears the
    merge gate, so it is the one file that says whether a pull request is
    finished and nothing else in the sweep reads it. Open boxes are printed
    the way MEMORY_REPO's PR count is — work left is the normal state of a
    branch, not a finding — while a claim past Rule 3's twelve hours and a
    branch that never carried the file are reported."""
    if not owned(repo, number, body, setup):
        return []
    head = (heads(repo, cache).get(number)
            or get(repo, f"pulls/{number}"))["head"]["sha"]
    text = contents(repo, "TODO.md", head)
    if text is None:
        return [] if cleared(repo, head, cache) else [
            f"#{number} never carried a TODO.md, so it cannot reach sign-off: "
            + body["html_url"]]
    boxes = [(mark.group(1).strip(), line) for line in text.splitlines()
             for mark in [BOX.match(line)] if mark]
    if opened := [line for mark, line in boxes if not mark]:
        print(f"{repo}#{number}: {len(opened)} of {len(boxes)} TODO.md"
              " point(s) open", file=sys.stderr)
    findings = []
    for mark, line in boxes:
        if "WIP" not in mark.upper():
            continue
        when = claimed(line)
        age = None if when is None else (
            datetime.datetime.now(datetime.timezone.utc) - when)
        if age is not None and age < STALE:
            continue
        findings.append(
            f"#{number} stale [WIP] claim, "
            + ("no readable date" if age is None else
               f"{when:%Y-%m-%d} ({elapsed(age)} old)")
            + ", reclaim it: " + body["html_url"])
    return findings


def item(repo, number, setup, cache):
    """The findings on one PR or issue: USER's APPROVE_EMOJI on the body or on
    any comment, and every thread where USER spoke last. GitHub splits comments
    across two endpoints, review comments threaded by in_reply_to_id and the
    conversation tab flat; both are swept, and so are the bodies. A body USER
    wrote is the thread when nothing else was said on it, which is the shape a
    standing order arrives in; once anyone comments, that thread's last word
    answers for it and the body would only report it twice.

    No `since` on either: unanswered is a condition rather than an event, so a
    window hides a question that is still open as readily as an answered one,
    and one turn sweeping past a comment loses it for good. `answered` is what
    makes the finding go quiet, and anyone replying is enough."""
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
        if not answered(asked, setup):
            findings.append(
                f"#{number} unanswered {setup['USER']} comment:"
                f" {asked['html_url']}" + seen(repo, kind, asked, setup, cache))
    kind = f"issues/{number}/reactions"
    if not threads and not answered(body, setup):
        findings.append(
            f"#{number} unanswered {setup['USER']}"
            f" {'pull request' if 'pull_request' in body else 'issue'}:"
            f" {body['html_url']}" + seen(repo, kind, body, setup, cache))
    return findings + todo(repo, number, body, setup, cache)


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
        findings += item(repo, number, setup, cache)
    return findings


def main(arguments):
    since = ""  # ISO 8601 UTC sorts lexicographically, so "" is the epoch
    if arguments and arguments[0] == "--since":
        _, since, *arguments = arguments
    findings = sweep(arguments[0], [int(n) for n in arguments[1:]], since,
                     config(CONFIG))
    print("\n".join(findings) if findings else "clean", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
