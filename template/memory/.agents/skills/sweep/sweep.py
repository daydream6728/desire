#!/usr/bin/env python3
"""Sweep open PRs and issues for USER signal the pipeline has not acted on:
bodies and threads where USER spoke last, APPROVE_EMOJI reacts from USER, the
issues closed inside the window, MEMORY_REPO's open-PR count, the state of
each AGENT-owned `TODO.md`, the review threads of an AGENT-owned pull request
that wait on an agent, whether its checks ran against its own base's tip and
whether every open item of a WORK_REPO has its `WORK/<repo>/<number>.md` note
in MEMORY_REPO. A finding is marked 👀 when the
pipeline has reacted to say it received it. config.env is the ground truth for
USER, the repos and the emoji, and it sits at the root of this clone;
AGENTS.md's rules say what to do with a finding.

Usage: sweep.py [--since <ISO8601 UTC, e.g. 2026-08-18T00:00:00Z>]
                [<owner/repo> [number...]]
       # no repo: every repo in play, i.e. MEMORY_REPO, DESIRE_REPO and
       #          every WORK_REPO, which is the only invocation that can
       #          print "clean"
       # no numbers: every open PR and issue; --since windows the closes
       # and quiets a question the pipeline already 👀'd
The last line is the verdict, and `clean` is a claim about the whole
configuration: it is printed only when the invocation covered every repo in
play, read all of them and found nothing. Anything narrower says what it did
cover and names what it left out, since twenty-two turns read `clean` off
three of four WORK_REPOS as though it covered the fourth (desire#30).
Exit 1 with one line per finding, exit 2 when a repo in play could not be read
— an incomplete sweep is neither clean nor a finding, and reading it as clean
is how a live 🚀 goes unanswered — and exit 0 otherwise. A read nobody answered
is retried before it counts as unreadable, since one dropped connection in
some two hundred used to end the run with a traceback, i.e. on exit 1.
Open `TODO.md` boxes are printed as context and do not make the sweep dirty.
"""
import base64
import datetime
import http.client
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

# The failures that mean nobody answered, as against GitHub answering no. The
# difference runs through this whole file — a 403 is raised so that a listing
# nobody read can never pass for an empty one — and a dropped connection is the
# other side of it: there is no answer to misread, only a read to do again.
# `urllib` wraps what fails while it sends the request in `URLError` and leaves
# what fails while it reads the response bare, so `http.client`'s own
# exceptions have to be named or they escape the guards written for exactly
# them: a `RemoteDisconnected` is a `ConnectionResetError` and an
# `HTTPException`, and neither is a `URLError`.
TRANSPORT = (urllib.error.URLError, http.client.HTTPException,
             ConnectionError, TimeoutError)
ATTEMPTS = 4      # one read and three retries, which a sweep can afford
BACKOFF = 2.0     # seconds before the first retry, doubling after it
BOX = re.compile(r"^\s*[-*] \[([^]]*)\]")
CLAIM = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?"
                   r"(?:Z|[+-]\d{2}:?\d{2})?)?")
STALE = datetime.timedelta(hours=12)
CONFIG = pathlib.Path(__file__).parents[3] / "config.env"
FOOTER_LINK = re.compile(r"\[[^\]]*\]\((https://[^\s)]+)\)")


def find_config():
    """`config.env` at the root of the clone this file lives in. This script
    is in MEMORY_REPO because the config is, so there is nothing to search
    for: one is three directories up from the other, in the live repo and in
    the template alike. AGENTS_CONFIG overrides, which is how the tests point
    at one of their own."""
    return pathlib.Path(os.environ.get("AGENTS_CONFIG") or CONFIG)


def config(path):
    """config.env as a dict, so that the pipeline is configured in one place
    and this script hard-codes no repo and no agent. A value is everything
    after the first `=`; WORK_REPOS is a comma-separated list and ADOPTED_PRS
    space-separated `repo:number,number` entries; AGENT_FOOTERS a
    comma-separated list of the markers that identify an agent-authored post,
    each one current. Blank lines and `#` comments are skipped — the file is
    written by hand and the seed ships commented — while any other line
    carrying no `=` raises rather than parsing to a key nothing will look up,
    and a key the file does not set is absent, so a caller reading it raises
    too."""
    setup = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"config.env: no key in {line!r}")
        setup[key.strip()] = value.strip()
    if "WORK_REPOS" in setup:
        setup["WORK_REPOS"] = setup["WORK_REPOS"].split(",")
    if "AGENT_FOOTERS" in setup:
        setup["AGENT_FOOTERS"] = [
            marker.strip() for marker in setup["AGENT_FOOTERS"].split(",")
            if marker.strip()]
    if "ADOPTED_PRS" in setup:
        setup["ADOPTED_PRS"] = {
            repo: [int(number) for number in numbers.split(",") if number]
            for entry in setup["ADOPTED_PRS"].split()
            for repo, _, numbers in [entry.partition(":")]}
    return setup


def read(request):
    """One REST read, retried while nobody has answered it.

    An `HTTPError` is GitHub answering and is raised at once, unretried, so
    that every status code in this file keeps the meaning its caller reads off
    it. A transport failure is the opposite case and the only one retried: a
    sweep of every repo in play is some two hundred reads, and discarding all
    of them because the one hundred and eighty-third was dropped costs the turn
    its only instrument. Measured rather than feared — on 2026-10-07 a
    `RemoteDisconnected` on `pulls/<n>/comments` ended a bare invocation with a
    traceback, three findings in, before discopy's pull requests were read at
    all.

    When the last attempt fails too the failure is raised, where `main` names
    the repo unreadable and the sweep exits 2: an incomplete sweep is neither
    clean nor a finding, whether the silence lasted one read or four."""
    for attempt in range(ATTEMPTS):
        try:
            with urllib.request.urlopen(request) as response:
                return json.load(response)
        except urllib.error.HTTPError:
            raise
        except TRANSPORT:
            if attempt + 1 == ATTEMPTS:
                raise
            time.sleep(BACKOFF * 2 ** attempt)


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
        items = read(request)
        if not isinstance(items, list):  # a single issue, comment or user
            return items
        results += items
        if len(items) < 100:
            return results
        page += 1


def review_comments(repo, number, body):
    """An issue has no review comments, and the item itself says so: GitHub
    numbers issues and pull requests in one space and puts a `pull_request`
    key on the ones that are pulls, which `item` has already read. So the
    pulls/ endpoint is never asked about an issue at all, rather than asked
    and forgiven a 404.

    That distinction used to be the status code, and it is not ours to
    rely on: behind a gateway the same request answers 403, which this
    raises — rate-limited or forbidden is a listing nobody read, and
    swallowing it as no comments is what makes an unreadable thread look
    answered. Reading it as "not a pull request" instead would be the same
    bug wearing the other mask. Asking one fewer request per issue is the
    smaller half of the reason."""
    if "pull_request" not in body:
        return []
    return get(repo, f"pulls/{number}/comments")


def resolutions(repo, number):
    """Every review thread of a pull request with its `resolved` flag, or
    `None` when this runtime cannot read one.

    Resolution state is not in GitHub's own REST API — it is a GraphQL field,
    and GraphQL answers 403 from these sessions. That 403's body names the
    stand-in the gateway serves in its place, `pulls/<n>/ccr/review_threads`,
    which returns each thread's `resolved`, `path` and `comment_ids` over
    plain REST. Four boards said this check was impossible; the route was in
    the error message all along.

    A runtime without that gateway gets a 404 here, and `None` says so rather
    than an empty list: no thread is not the same claim as no answer, and the
    caller turns `None` into a finding, so the condition reads as unchecked on
    such a runtime instead of silently passing."""
    try:
        return get(repo, f"pulls/{number}/ccr/review_threads")
    except urllib.error.HTTPError as error:
        if error.code in (403, 404):
            return None
        raise


def waiting(threads, comments, setup):
    """The last word of every review thread that waits on an agent, which is
    `AGENTS.md`'s third sign-off condition read backwards: a pull request is
    ready when every thread is resolved or waiting on human feedback, so the
    threads reported here are the ones that are neither.

    Ours is the word that carries an AGENT_FOOTERS marker; a thread we spoke
    last on waits on a human and is not a finding. USER's own last word is
    left to `asking`, which already reports it and lets a 👀 quiet it — this
    would only say it twice. Everything else — a review bot, a human other
    than USER — is a thread whose ball is in our court, however old.

    An unresolved thread none of whose comments appear in the listing is
    reported too. It is rare, and it is the one case where the honest answer
    is that we cannot tell who spoke last: treating unreadable as resolved is
    the mistake this whole function exists to stop making."""
    waits = []
    for thread in threads:
        if thread["resolved"]:
            continue
        known = [comments[number] for number in thread["comment_ids"]
                 if number in comments]
        spoke = max(known, default=None,
                    key=lambda comment: comment["created_at"])
        if spoke is None or (answered(spoke, setup)
                             and not agent_footer(spoke["body"], setup)):
            waits.append((thread, spoke))
    return waits


def signed_off(repo, number, body, review, setup):
    """The threads standing between an AGENT-owned pull request and sign-off.

    `AGENTS.md` asks three things of a ready head: no `TODO.md`, green CI, and
    no review thread waiting on an agent. `todo` checks the first, CI is read
    off the check runs, and until today nothing checked the third — so it was
    enforced by whichever turn happened to open the head and look. On that
    record, discopy #752 on 09-09, #660 on 09-12 and #662 on 09-15 were each
    called ready with a thread open on them, every one found by accident."""
    if not owned(repo, number, body, setup):
        return []
    threads = resolutions(repo, number)
    if threads is None:
        return [f"#{number} sign-off condition 3 is unchecked here: this"
                " runtime serves no pulls/<n>/ccr/review_threads, so whether"
                " a review thread waits on an agent is unknown: "
                + body["html_url"]]
    comments = {comment["id"]: comment for comment in review}
    return [f"#{number} review thread waiting on an agent"
            f" ({thread['path']}): "
            + (spoke["html_url"] if spoke else body["html_url"])
            for thread, spoke in waiting(threads, comments, setup)]


def check_runs(repo, head, cache):
    """The check runs on a commit, once per head. The listing is a mapping
    rather than an array, so `get` returns its first page whole: a head with
    more than a hundred runs would read short, and none of ours has ten."""
    if head not in cache.setdefault("runs", {}):
        cache["runs"][head] = get(
            repo, f"commits/{head}/check-runs").get("check_runs", [])
    return cache["runs"][head]


def arrears(repo, pull, cache):
    """How many commits the head's **own** base has that the head lacks, with
    that base's tip, or `(None, None)` when GitHub will not compare the two.

    This is `AGENTS.md`'s second sign-off condition read exactly rather than
    through a clock. A `pull_request` job checks out `refs/pull/N/merge`, the
    head merged with its base as of the checkout; when the base's tip is
    already an ancestor of the head, that merge **is** the head, so a green run
    on the head's sha is green *with the target branch merged in*. One commit
    of arrears and it is not: the ticks are green and they attest to a merge
    nobody will ever perform.

    The base is the head's **own** ref — `split/3`, not `main` — which is the
    whole of desire#32: every behind-count in that stack was right about `main`
    and silent about the base that had moved. desire#32 proposed reading two
    timestamps and calling a green stale when it predates the base's tip; one
    `compare` carries the count and the tip together, so the same question is
    answered by an ancestry rather than by a proxy for one, at the same price.
    """
    key = (pull["base"]["ref"], pull["head"]["sha"])
    if key not in cache.setdefault("arrears", {}):
        try:
            compared = get(repo, "compare/{}...{}".format(*key))
            cache["arrears"][key] = (compared["behind_by"],
                                     compared["base_commit"]["sha"])
        except urllib.error.HTTPError as error:
            if error.code not in (403, 404, 422):
                raise
            cache["arrears"][key] = (None, None)
    return cache["arrears"][key]


def unmerged(count, base, noted):
    """Why sign-off condition 2 may fail on a head, or `None` when it holds —
    two sentences rather than one, the way `staleness` splits its pair.

    Arrears against its own base is the **head's** failure: no job has ever
    seen the tree USER would merge, so its green says nothing about it, and
    what it wants is a merge-down and a round. A note recording another base is
    the **note's** failure and wants a re-read rather than a push: the head is
    current and what is written down about it is not."""
    if count:
        return (f"is {count} commit(s) behind its own base {base[:7]}, so"
                " every check on it ran against a merge nobody will perform"
                " — condition 2 is stale, not green")
    if noted and not (base.startswith(noted) or noted.startswith(base)):
        return (f"is current, and its note still records base {noted} where"
                f" the base is now {base[:7]} — re-read the note, not the head")
    return None


def condition_two(repo, number, body, setup, cache):
    """`AGENTS.md`'s second sign-off condition on one AGENT-owned pull request:
    *CI is green on the real jobs, with the target branch merged in.*

    Nothing checked it until now, so it was enforced by whichever turn happened
    to open the head and look — the footing condition 3 was on before
    `signed_off`, and with the same result: three notes and two boards called
    discopy#660 ready between 09-16 and 09-19 while its own base had moved
    three commits and no job had seen that tree (desire#32).

    Greenness itself is not read here. The sweep cannot know which checks a
    repository expects — `cubic` is an extra, `proptest` is opt-in by label,
    `guard` does not run on a stacked head — so a conclusion is left to the
    turn that enumerates them, and what is mechanical is whether the runs that
    exist ran against the right tree. A head carrying no run at all is printed
    as context rather than reported: DESIRE_REPO runs no CI, so every head
    there would otherwise be a finding for good."""
    if not owned(repo, number, body, setup):
        return []
    pull = heads(repo, cache).get(number) or get(repo, f"pulls/{number}")
    count, base = arrears(repo, pull, cache)
    if base is None:
        return [f"#{number} sign-off condition 2 is unchecked here: GitHub"
                " would not compare its head to its base"
                f" {pull['base']['ref']!r}, so whether its checks ran against"
                " the merge is unknown: " + body["html_url"]]
    if not check_runs(repo, pull["head"]["sha"], cache):
        print(f"{repo}#{number}: no check run on its head, so condition 2 is"
              f" unattested rather than green ({count} behind base"
              f" {base[:7]})", file=sys.stderr)
        return []
    why = unmerged(count, base, noted_base(repo, number))
    return [] if why is None else [f"#{number} {why}: " + body["html_url"]]


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


def agent_footer(body, setup):
    """Whether `body`'s last line is one of AGENT_FOOTERS.

    There is no single signature and there cannot be: the marker is whatever
    each agent's own runtime appends, which the agent does not choose. Claude
    Code emits `_Generated by [Claude Code](https://claude.ai/code)_` on every
    post it makes, Codex emits its own line, and both mean the same thing —
    AGENT posted this from USER's handle. So every marker in the list is
    current, none is historical, and retiring one is what would make our own
    replies read as USER's unanswered questions.

    A marker counts two ways and no others: as the whole final line, or inside
    the HTTPS target of a Markdown link on that line — which is how a URL token
    matches the footer wrapping it. A link's *label* never counts, however
    exactly it reads: `[Generated by Codex](https://anywhere-at-all)` would
    otherwise let any destination silence a thread, and the label is the half a
    human types. A runtime that wants its linked footer recognised puts the URL
    token in this list, the way `claude.ai/code` already is. Nor does a marker
    count in prose: a line merely mentioning one is a human writing about the
    convention, not an agent following it.
    """
    line = ((body or "").strip().splitlines() or [""])[-1].strip().strip("_*")
    targets = FOOTER_LINK.findall(line)
    return any(line == marker or any(marker in target for target in targets)
               for marker in setup.get("AGENT_FOOTERS", []) if marker)


def answered(comment, setup):
    """Whether anyone but USER wrote this, the footer deciding for an agent
    post from USER's account. An issue with no description has a `None` body."""
    return (comment["user"]["login"] != setup["USER"]
            or agent_footer(comment["body"], setup))


def asking(repo, kind, target, setup, since, cache):
    """The 👀 flag when `target` is a question of USER's still waiting on us,
    `None` when it is not: either somebody answered it, or the pipeline reacted
    👀 to say it is in hand and `since` puts it before the window. Unanswered is
    a condition rather than an event, so the window never hides one on its own —
    a sweep with no `--since` reports every last question, and a 👀 is what
    quiets an old one."""
    if answered(target, setup):
        return None
    flag = seen(repo, kind, target, setup, cache)
    return None if flag and target["created_at"] < since else flag


def memory(repo):
    """MEMORY_REPO holds one open PR per day, checked whatever the window since
    it is an invariant rather than a delta. Several open at once is USER not
    having merged the past days, which is theirs and no finding of ours; two
    under one title is a day written twice, which is ours. The count and the
    URLs are printed either way, so a turn sees what is waiting to be merged
    without the sweep calling it dirty. When any are open the newest is named
    as the branch to cut a new day's PR from, not `main`, so unmerged days
    stack rather than conflict on `README.md`/`USER_TODO.md` (desire#144)."""
    open_prs = get(repo, "pulls?state=open")
    print(f"{repo}: {len(open_prs)} open PR(s)"
          + "".join("\n  " + pr["html_url"] for pr in open_prs), file=sys.stderr)
    if open_prs:
        newest = max(open_prs, key=lambda pull: pull["created_at"])
        print(f"{repo}: base a new day's PR on {newest['head']['ref']!r}"
              f" ({newest['title']!r}, the newest still open), not main, so"
              " unmerged days stack rather than conflict (desire#144)",
              file=sys.stderr)
    days = {}
    for pull in open_prs:
        days.setdefault(pull["title"], []).append(pull["html_url"])
    return [f"{repo}: {len(urls)} open PRs titled {title!r}, one a day is the"
            " rule — push to one and close the rest: " + ", ".join(urls)
            for title, urls in days.items() if len(urls) > 1]


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
    branch that never carried the file are reported.

    A branch that never carried one broke `RULES.md` 1, which asks every agent
    branch to open one, and that is all it broke: `RULES.md` 2 settles the
    readiness question the other way — *"a branch that never carried one keeps
    whatever state its author gave it. Read the boxes, not the badge."* There
    are no boxes, so nothing is pending. Saying such a head "cannot reach
    sign-off" put a merge gate in front of discopy#763 that no rule asks for."""
    if not owned(repo, number, body, setup):
        return []
    head = (heads(repo, cache).get(number)
            or get(repo, f"pulls/{number}"))["head"]["sha"]
    text = contents(repo, "TODO.md", head)
    if text is None:
        return [] if cleared(repo, head, cache) else [
            f"#{number} never carried a TODO.md, so it never opened one to"
            " work from (RULES.md 1); its readiness is untouched (RULES.md 2): "
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


def item(repo, number, setup, since, cache):
    """The findings on one PR or issue: USER's APPROVE_EMOJI on the body or on
    any comment, and every thread where USER spoke last. GitHub splits comments
    across two endpoints, review comments threaded by in_reply_to_id and the
    conversation tab flat; both are swept, and so are the bodies. A body USER
    wrote is the thread when nothing else was said on it, which is the shape a
    standing order arrives in; once anyone comments, that thread's last word
    answers for it and the body would only report it twice. `asking` decides
    which of the two are still waiting on us."""
    findings, threads, body = [], {}, get(repo, f"issues/{number}")
    kind = f"issues/{number}/reactions"
    if approved(repo, kind, body, setup, cache):
        findings.append(
            f"#{number} {setup['APPROVE_EMOJI']} from {setup['USER']} on the"
            f" body: {body['html_url']}" + seen(repo, kind, body, setup, cache))
    review = review_comments(repo, number, body)
    comments = [(comment, comment.get("in_reply_to_id", comment["id"]), "pulls")
                for comment in review]
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
        flag = asking(repo, kind, asked, setup, since, cache)
        if flag is not None:
            findings.append(
                f"#{number} unanswered {setup['USER']} comment:"
                f" {asked['html_url']}" + flag)
    kind = f"issues/{number}/reactions"
    flag = None if threads else asking(repo, kind, body, setup, since, cache)
    if flag is not None:
        findings.append(
            f"#{number} unanswered {setup['USER']}"
            f" {'pull request' if 'pull_request' in body else 'issue'}:"
            f" {body['html_url']}" + flag)
    return (findings + signed_off(repo, number, body, review, setup)
            + condition_two(repo, number, body, setup, cache)
            + todo(repo, number, body, setup, cache))


def notes(have, want):
    """The two ways `WORK/` and the live open items disagree: an item nobody
    wrote a note for, and a note whose item is merged or closed. Pure, because
    it is the whole rule — the board's queue drifted for a week precisely
    because no test could be written against a paragraph of prose."""
    return sorted(want - have), sorted(have - want)


def stale(read, updated):
    """The notes whose item moved after the note was last read, by whole days:
    a note read on the morning its head is pushed to is current, one carrying
    last week's date over a head that moved yesterday is not. `read` maps a
    number to the date its note states, `updated` to the item's `updated_at`.
    A note with no readable date is stale by construction — it cannot say when
    it was true — and `staleness` gives it its own sentence, since what it
    wants is a date rather than a re-read."""
    return sorted(number for number, day in read.items()
                  if number in updated
                  and (day is None or day < updated[number][:10]))


READ = re.compile(r"\bread\s+\**(\d{4}-\d{2}-\d{2})")


def read_date(text):
    """The date a `WORK/` note says it was read, `None` when it carries none.

    The field is `read <date>`, and a note is prose around it: a 100-column
    fill wraps the date onto the next line, a turn double-spaces it, and one
    wrote `read **2026-09-25 00:3xZ**` to make the freshest fact on the line
    stand out. All three are the field, so any whitespace and any emphasis
    between the two is accepted. Prose between them is not — `re-read live
    2026-09-18` names no field and reads as undated — and neither is a date
    with no `read` in front of it, which is every other date in a note's log.

    Undated is reported as such: it is stale by construction, since a note
    that cannot say when it was true cannot say it is current, but what it
    wants is a date written rather than its head re-read (desire#31)."""
    match = READ.search(text)
    return match.group(1) if match else None


def staleness(number, day):
    """Why a note may be stale, which is two findings rather than one. Both
    used to print through the sentence of the second, so a note carrying no
    readable date was reported as `was read None and 489 moved since`: the
    turn reading it re-read a head that had not moved, or edited a date that
    was already right — three notes in one night, which is desire#31."""
    return ("carries no read date, so nothing says when it was true — write"
            " one" if day is None else
            f"was read {day} and {number} moved since, so it may be stale")


BASE = re.compile(r"\bbase\s+[*`]*([0-9a-f]{7,40})\b")


def base_sha(text):
    """The base sha a `WORK/` note records its checks as having run against,
    `None` when it carries none.

    The field is `base <sha>` on the **state** line, beside the `head <sha>`
    the notes already carry, and it is parsed the way `read <date>` is: through
    the emphasis and the backticks a note dresses a sha in, and nothing else.
    The base *ref* is named elsewhere on the line — `0 behind `main`` says it
    once — because `base `main`@`4d96025`` would put prose between the field
    and its value, which this refuses on purpose: a field is one shape or it is
    not parsed at all. An abbreviation is a prefix and compares as one."""
    match = BASE.search(text)
    return match.group(1) if match else None


def noted_base(repo, number):
    """The base sha `WORK/<repo>/<number>.md` records, `None` when there is no
    note or it carries no such field.

    Carrying none is silent and never a finding. The arithmetic in `arrears` is
    live and needs no note at all; the field exists so that a *reader* of the
    note can do it too, the way `read <date>` lets one date a fact without
    asking GitHub. Every note written before desire#32 has none, and a finding
    on each would drown the one note that is actually wrong."""
    root = memory_clone()
    if root is None:
        return None
    note = root / "WORK" / repo.split("/")[-1] / f"{number}.md"
    return base_sha(note.read_text()) if note.is_file() else None


CITE = re.compile(r"(?P<where>[\w.-]+(?:/[\w.-]+)?)?#(?P<number>\d+)")


def cited(repo, texts):
    """Every `#<number>` an existing note mentions **of this repo**. Forming a
    view on one item pulls in what it references, which is how an issue earns
    a note without a human deciding it has: a note that says a head waits on a
    ruling names the issue, and that issue is then in play.

    A citation carrying a repo belongs to that repo, not to this one. Bare
    `#26` is this one's, and so are `discopy#26` and `discopy/discopy#26` when
    sweeping `discopy/discopy`; `desire#26` is somebody else's. Matching the
    number alone made `WORK/discopy/661.md`, which cites `desire#26`, demand a
    note for discopy's own unrelated #26 — one finding a night that no turn
    could act on, and noise a real one can hide behind."""
    name = repo.split("/")[-1]
    return {int(match["number"]) for text in texts
            for match in CITE.finditer(text)
            if match["where"] in (None, repo, name)}


def memory_clone():
    """Where MEMORY_REPO is checked out: the directory holding the `config.env`
    we are configured by, since that file lives at its root — normally the
    clone this script is in. `None` when it carries no `WORK/`, so a sweep run
    against a memory repo that has no notes yet still sweeps, cannot check
    them, and says so rather than reporting every item as missing one."""
    root = find_config().parent
    return root if (root / "WORK").is_dir() else None


def uncharted(repo, setup, cache):
    """What `WORK/<repo>/` and the repo's open items say about each other.

    The notes cover the whole repository, not our own slice of it: someone
    else's pull request collides with ours, and an issue nobody answered is
    the reason a head is stuck. Ownership is a field inside the note, not a
    condition on it existing.

    A note is **required** for every open pull request, and for every open
    issue an existing note cites — forming a view on one item is what pulls in
    what it references. Every other open issue is printed as context and does
    not make the sweep dirty: a note that only restated GitHub would be the
    board's queue again, one file per row instead of one table.

    Three findings: an item with no note, a note whose item is closed, and a
    note older than the item it describes."""
    if repo not in setup["WORK_REPOS"]:
        return []  # the rule binds where the work happens
    root = memory_clone()
    if root is None:
        print(f"{repo}: MEMORY_REPO carries no WORK/, notes unchecked",
              file=sys.stderr)
        return []
    name = repo.split("/")[-1]
    directory = root / "WORK" / name
    files = {int(note.stem): note for note in directory.glob("*.md")
             if note.stem.isdigit()} if directory.is_dir() else {}
    texts = {number: note.read_text() for number, note in files.items()}
    read = {number: read_date(text) for number, text in texts.items()}
    items = get(repo, "issues?state=open")
    updated = {item["number"]: item["updated_at"] for item in items}
    pulls = {item["number"] for item in items if "pull_request" in item}
    want = pulls | (cited(repo, texts.values()) & set(updated))
    unread = sorted(set(updated) - want - set(files))
    if unread:
        print(f"{repo}: {len(unread)} open issue(s) nobody has a note on, none"
              " of them cited by one: "
              + ", ".join(f"#{number}" for number in unread), file=sys.stderr)
    missing, _ = notes(set(files), want)
    _, orphan = notes(set(files), set(updated))  # open at all, not required
    link = f"https://github.com/{repo}/issues/"
    return [f"{repo}#{number} has no WORK/{name}/{number}.md, so nothing says"
            f" where it stands: {link}{number}" for number in missing
            ] + [f"{repo}: WORK/{name}/{number}.md outlived its item, which is"
                 f" closed — delete it: {link}{number}" for number in orphan
            ] + [f"{repo}: WORK/{name}/{number}.md "
                 + staleness(number, read[number]) + f": {link}{number}"
                 for number in stale(read, updated)]


def sweep(repo, numbers, since, setup):
    """One line per finding, empty when the sweep is clean.

    Every finding names its own repo. One invocation now covers several
    (desire#30), so a line opening on a bare `#659` would not say whose, and
    the per-item findings are written that way throughout: the repo goes on
    here, in one place, rather than in each of the nine that build one."""
    cache, findings = {}, []
    if repo == setup["MEMORY_REPO"] and not numbers:
        findings += memory(repo)
    if not numbers:
        findings += uncharted(repo, setup, cache)
        findings += closed_since(repo, since)
        numbers = sorted({
            issue["number"] for issue in get(repo, "issues?state=open")})
    for number in numbers:
        findings += item(repo, number, setup, since, cache)
    return [f"{repo}{finding}" if finding.startswith("#") else finding
            for finding in findings]


def everywhere(setup):
    """Every repo in play, as `AGENTS.md` means it: MEMORY_REPO first, because
    its day PR is where the turn writes; then DESIRE_REPO, whose `main` is the
    rules; then the WORK_REPOS, where the work happens. De-duplicated, since
    DESIRE_REPO is normally one of the WORK_REPOS too, and order-preserving, so
    that two turns read the same list in the same order.

    Nothing iterated this list before (desire#30): `config()` parsed it and
    both readers were membership tests on the repo the agent had already typed,
    so a repo added to `config.env` was swept by nobody until somebody happened
    to type it, and a turn was never told the configuration had moved."""
    named = [setup.get("MEMORY_REPO"), setup.get("DESIRE_REPO"),
             *setup.get("WORK_REPOS", [])]
    return list(dict.fromkeys(repo for repo in named if repo))


def coverage(asked, numbers, unreadable, findings, setup):
    """The verdict line, and the only thing a turn may read as licence to
    conclude "no unblocked work".

    `clean` says the configuration is clean, so it needs all three: every repo
    in play asked about, every one of them read, and no finding in any. A
    sweep of one repo is not a sweep of the others and a sweep of two items is
    not a sweep of the repo, so anything narrower names its own scope and what
    it left out instead — the denial that was invisible in the output for
    twenty-two turns (desire#30)."""
    swept = [repo for repo in asked if repo not in unreadable]
    missed = [repo for repo in everywhere(setup) if repo not in asked]
    if not (numbers or unreadable or missed or findings):
        return "clean"
    scope = ", ".join(swept) + "".join(f" #{number}" for number in numbers)
    parts = [f"{len(findings)} finding(s)" if findings else "no finding",
             f"in {scope}" if swept else "anywhere: nothing was read"]
    return "; ".join([" ".join(parts)] + [
        f"{label}: {', '.join(repos)}"
        for label, repos in [("unreadable", unreadable),
                             ("not asked about", missed)] if repos])


def main(arguments):
    since = ""  # ISO 8601 UTC sorts lexicographically, so "" is the epoch
    if arguments and arguments[0] == "--since":
        _, since, *arguments = arguments
    setup = config(find_config())
    asked = [arguments[0]] if arguments else everywhere(setup)
    numbers = [int(number) for number in arguments[1:]]
    findings, unreadable = [], []
    for repo in asked:
        try:
            findings += sweep(repo, numbers, since, setup)
        except TRANSPORT as error:
            unreadable.append(repo)
            print(f"{repo}: GitHub unreadable, the sweep is incomplete and"
                  f" says nothing about this repo: {error}", file=sys.stderr)
    print("\n".join(findings
                    + [coverage(asked, numbers, unreadable, findings, setup)]),
          file=sys.stderr)
    return 2 if unreadable else 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
