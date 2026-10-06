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
`.agents/skills/sweep/sweep.py [--since <ISO8601>] [<owner/repo> [number...]]`. It flags every
APPROVE_EMOJI react from USER on a body or a comment across both endpoints, and every thread where
USER spoke last — a thread is answered when anyone other than USER has replied since, and which
agent closed it does not matter. Every finding names its own repo, since one invocation can cover
several.

**With no repo argument it sweeps every repo in play** — MEMORY_REPO, DESIRE_REPO and every
WORK_REPO, de-duplicated in that order — which is the only invocation that can print `clean`. The
last line is the verdict and `clean` is a claim about the configuration, not about whatever the
agent typed: a narrower invocation prints what it covered and names the configured repos it was
never asked about, and a repo it could not read is one line among the findings rather than the whole
run's answer, so one denial cannot hide what the readable repos found. Exit 2 when a repo in play
could not be read, 1 on findings, 0 otherwise — so sweeping one slow repo at a time stays exit 0 and
the verdict line is what says it covered one of four. Before this, `WORK_REPOS` was parsed and never
iterated, so a repo added to `config.env` was swept by nobody until somebody happened to type it,
and twenty-two turns read `clean` off three of four ([#30](https://github.com/daydream6728/desire/issues/30)).

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

It reads `WORK/` against the live open items three ways: an open item with no note, a note whose
item is closed, and a note older than the item it describes. The last is arithmetic on the note's
own `read <date>` field, parsed through any whitespace and any emphasis — `read **2026-09-25**` and
a date wrapped onto the next line are both the field, prose between the two is not. A note carrying
no date the parser can see is reported as carrying none rather than as read `None`: it is stale by
construction, and what it wants is a date written, where an old date wants its head re-read.

On those same heads it checks the second sign-off condition — *CI green on the real jobs, **with the
target branch merged in***. One `compare` of the head against its **own** base ref answers it
exactly: a `pull_request` job checks out `refs/pull/N/merge`, the head merged with its base as of
the checkout, so a head whose base tip is already an ancestor of it has checks that ran on the tree
USER would merge, and a head one commit behind has checks that attest to a merge nobody will
perform. The finding names the count and the base's tip. **Greenness is not read**: the sweep cannot
know which checks a repository expects — `cubic` is an extra, `proptest` is opt-in by label, `guard`
does not run on a stacked head — so a conclusion stays with the turn that enumerates them, and what
is mechanical is whether the runs that exist ran against the right tree. A head carrying **no** run
is printed as context rather than reported, since DESIRE_REPO runs no CI. The same check reads the
note's `base <sha>` field, so that a head owing a merge-down and a note owing a re-read are two
findings rather than one: a note carrying no such field is silent, and every note written before
this existed carries none.

On those same heads it checks the third sign-off condition — *no review thread waiting on an agent*.
A thread is a finding when it is unresolved and its last word is neither ours nor USER's: a review
bot or another human is waiting on us, while a thread we replied to last waits on a human and USER's
own last word is already reported as an unanswered question, with a 👀 to quiet it. Resolution state
is not in GitHub's REST API and GraphQL answers 403 from these sessions; the 403's own body names
the gateway's REST stand-in, `pulls/<n>/ccr/review_threads`, which is what the sweep reads. A
runtime that serves no such route reports the condition **unchecked** rather than clean, since an
unreadable thread and a settled one are not the same claim.

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
Commits are signed through whichever key the session has, both registered on AGENT's account. The
environment's setup script imports a passphrase-free GPG key and sets `gpg.format openpgp`,
`user.signingkey` and `commit.gpgsign`, which covers every session of that environment; the
setup script sees none of the environment's variables, so the key is in the script itself, and
the identity comes from `GIT_CONFIG_*` variables, read after every config file and so after the
default identity the environment writes to `~/.gitconfig` once the script is done. Without it,
the SessionStart hook signs from `AGENTS_SIGNING_KEY`, a passphrase-free SSH private key: it
installs `openssh-client` (git signs through `ssh-keygen -Y sign`), writes the key and sets
`commit.gpgsign`. The hook keeps a GPG config whose key is in the keyring and clears any other
global signing config, so no stale setting outlives its key; a session with neither key commits
unsigned rather than failing. Leaked, either key can only forge the badge — revoke it by deleting
it from AGENT's account. Key setup is in the README's Verified commits section.
