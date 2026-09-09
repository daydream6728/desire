# OPERATIONS.md

The machinery behind the rules in [`AGENTS.md`](AGENTS.md) — how each mechanism works and how to
recover when it doesn't. `CLAUDE.md` does not import it, so it is not loaded into every session:
read it when something misbehaves, or when you need the exact command or behaviour behind a rule.

## Finding config.env
Both readers reach `config.env` by a fixed relative path from their own location — nothing is
searched for and no repository name is hard-coded — with `AGENTS_CONFIG` overriding the path for
both. `session-start.sh` reads it before a turn's first commit to set the git identity; `sweep.py`'s
`config()` reads it before every sweep. A `config.env` that cannot be read clears the global git
identity rather than set a stale one, so committing fails loudly; the hook warns when the clearing
itself fails. The public copies under [`template/`](template) are the seed a new MEMORY_REPO is
built from, which is why a change to either reader lands in both the same turn.

## Measuring against git history
Before any behind-count or collision measurement, assert the clone is complete: `git rev-parse
--is-shallow-repository` must print `false`, else `git fetch --unshallow origin`. On a shallow clone
there is no merge base, so `git merge-tree` dies with exit 128 and no `CONFLICT` line — which reads
as no conflicts, the silent failure the assertion prevents.

## Reading the sweep
[`sweep.py`](template/memory/.agents/skills/sweep/sweep.py) runs from the MEMORY_REPO clone as
`.agents/skills/sweep/sweep.py [--since <ISO8601>] <owner/repo> [number...]`. It flags every
APPROVE_EMOJI react from USER on a body or a comment across both endpoints, and every thread where
USER spoke last — a thread is answered when anyone other than USER has replied since, and which
agent closed it does not matter.

`--since` reads the comments as a delta; widen the window after a turn runs late or dies. The sweep
also lists the issues closed inside the window with their `state_reason` and who closed them, since
closing an issue is an answer that leaves no thread. Reacts ignore `--since`: a 🚀 has no answered
state and is reported whatever its age until the thing it sits on closes. A USER question nobody has
answered is reported whatever its age too, unless the pipeline 👀'd it and it predates the window —
so a question landing between two sweeps is never lost, an old one goes quiet once a turn says it
received it, and a sweep with no `--since` reports the whole backlog.

The sweep marks a `👀` flag when anyone but USER has reacted, so a turn can tell a backlog from a
queue. React with `add_issue_comment`'s `reaction` on a body or conversation comment, and
`add_reply_to_pull_request_comment`'s on a review comment.

It also reads [`RULES.md`](RULES.md)'s `TODO.md` off every AGENT-owned head in WORK_REPOS: open
boxes as context, a claim past its twelve hours and a branch that never carried one as findings.

## Matching an attribution footer
A reply from USER counts as an agent's when its last line is one of AGENT_FOOTERS — as the whole
line, or inside the HTTPS *target* of a Markdown link on it (which is how a URL token matches the
footer wrapping it). A link's *label* never counts, since the label is the half a human types, so
accepting it would let any destination silence a thread; nor does a marker in prose, which is a
human writing about the convention. This is how the adopted PRs read.

A runtime whose footer links to a shareable session snapshot puts the URL token in AGENT_FOOTERS the
way `claude.ai/code` is, rather than relying on the label; the snapshot is opened and reviewed
before it is linked, and an internal session or thread ID is not a URL and must never be turned into
one.

## Commit signing
Commits are signed when the environment provides `AGENTS_SIGNING_KEY`, a passphrase-free SSH private
key whose public half is registered on AGENT's account as a **signing key**. The SessionStart hook
clears the global signing config so no stale setting outlives its key, installs `openssh-client`
(git signs through `ssh-keygen -Y sign`), writes the key and sets `commit.gpgsign`, so pushed
commits show Verified; a session without the variable commits unsigned rather than failing. Leaked,
the key can only forge the badge — revoke it by deleting the public half from AGENT's account. Key
setup is in the README's Verified commits section.
