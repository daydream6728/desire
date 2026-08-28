# Changelog

What landed on `main`, newest first — when each rule started binding, and what it replaced.
Entries state the changes, no explanation of why.

## 2026-08-26

**One memory PR per day, written by 🐦 Birdsong alone**
([#113](https://github.com/toumix/desire/pull/113), closes
[#112](https://github.com/toumix/desire/issues/112)) — `AGENTS.md`'s "one memory PR open at a
time" becomes one per day, titled with the day it covers and opened by Birdsong even when the
previous day's has not merged. `sweep.py`'s `memory` stops failing on more than one open PR and
fails on two sharing a title instead, printing the open PRs either way, in place of "at most one
is allowed — push to the oldest and close the rest".
`EVENING.md` gains "writes its turn file and one comment, never that PR's description",
`BIRDSONG.md` names Birdsong the only routine that writes it. The memory PR template's queue
stops being a table and links the board instead.

**An unanswered USER comment is reported until it is answered** (same PR, closes
[#111](https://github.com/toumix/desire/issues/111)) — `sweep.py`'s two unanswered branches ask
the new `asking` instead of their `created_at >= since` window: a question of USER's is reported
whatever its age unless the pipeline 👀'd it and it predates the window, and a sweep with no
`--since` reports every one. `closed_since` keeps its window. Reverses the windowing
[#90](https://github.com/toumix/desire/issues/90) introduced on the body branch. `AGENTS.md` says
what a 👀 now buys.

## 2026-08-24

**Agents delete their own `TODO.md` once every point is done**
([#108](https://github.com/toumix/desire/pull/108), closes
[#107](https://github.com/toumix/desire/issues/107)) — the `TODO.md` rule of `RULES.md` is split
in two: creation stays point 1, deletion becomes point 2, which replaces "never delete
it" with: once every point is `[x]` or filed as an issue, the agent deletes `TODO.md` itself,
clearing the merge gate and taking the pull request out of draft; a round of review feedback —
bot or human — starts a fresh one, the feedback quoted at the top and the fixes as boxes,
deleted again when the round is done; nitpicks are just fixed, pushed and resolved. The
never-alter-the-verbatim-prompt clause stays; same edit on discopy's copy in
[discopy#608](https://github.com/discopy/discopy/pull/608).

**Rule 4 is removed** (same PR) — only-talk-when-prompted and never-reply-unless-USER-replied-
or-🚀 are gone from `RULES.md`; `AGENTS.md`'s trusted-instructions section still binds the
routines. Same removal on discopy's copy in discopy#608.

**REVIEWER leaves the rules and the config** (same PR) — the tag-REVIEWER-once-done rule is
removed from `AGENTS.md` and `REVIEWER` from `config.env`; the summon now lives in
[discopy#608](https://github.com/discopy/discopy/pull/608)'s workflow. Supersedes the
public-repos-only scoping of [#86](https://github.com/toumix/desire/issues/86) built as
[#89](https://github.com/toumix/desire/pull/89).

## 2026-08-21

**The VM startup script wires the hook for multi-repo sessions**
([#104](https://github.com/toumix/desire/pull/104), closes
[#103](https://github.com/toumix/desire/issues/103)) — the environment's startup script writes
`/home/user/.claude/settings.json` pointing `SessionStart` at the hook by absolute path. The
snippet lands in the README's new Verified commits section, with the key setup — generate,
register as a signing key, paste into `AGENTS_SIGNING_KEY`. Extends the two hook entries below,
same day.

**The hook starts unsigned by clearing the whole signing config**
([#101](https://github.com/toumix/desire/pull/101), closes
[#99](https://github.com/toumix/desire/issues/99)) — `session-start.sh` unsets `commit.gpgsign`,
`user.signingkey`, `gpg.format` and `gpg.ssh.program`, not `commit.gpgsign` alone, and pins
`gpg.ssh.program` to `ssh-keygen` when signing turns on, overriding the environment's own.
Amends the entry below, same day.

**Commits are signed** ([#97](https://github.com/toumix/desire/pull/97), closes
[#96](https://github.com/toumix/desire/issues/96)) — the SessionStart hook turns
`AGENTS_SIGNING_KEY`, an SSH key registered on AGENT's account as signing-only, into
`commit.gpgsign`, so commits show Verified; a session without the key commits unsigned.
Extends the commits-authored-by-AGENT entry of 2026-08-20 below.

## 2026-08-20

**The config lives in `config.env`** ([#94](https://github.com/toumix/desire/pull/94)) — `USER`,
`AGENT`, `AGENT_EMAIL`, `WORK_REPOS`, `MEMORY_REPO`, `DESIRE_REPO`, `APPROVE_EMOJI`, `REVIEWER`,
`AGENT_FOOTER` and `ADOPTED_PRS` are set there, one `KEY=value` per line, `CLAUDE.md` imports it
into every session, and `AGENTS.md`'s Config section points at it rather than naming them.
`session-start.sh` reads it to set `user.name` and `user.email` globally on every remote session,
before the first commit of a turn; `sweep.py`'s `config()` parses it. Replaces the Config block
of `AGENTS.md`.

**Commits are authored by AGENT and AGENT_EMAIL** ([#93](https://github.com/toumix/desire/pull/93),
closes [#92](https://github.com/toumix/desire/issues/92)) — `AGENT_EMAIL` joins the Config, set with
`AGENT` on every clone before a turn's first commit. New rule, replaces nothing.

**`RULES.md` lands here** (same PR, closes
[#91](https://github.com/toumix/desire/issues/91)) — a verbatim copy of discopy's, imported by
`CLAUDE.md`, until [#87](https://github.com/toumix/desire/issues/87) gives it one home. `sweep.py`
reads its `TODO.md` off each AGENT-owned head in WORK_REPOS: open boxes as context, a `[WIP]` claim
past twelve hours and a branch that never carried one as findings; a branch that carried one and
deleted it at the gate is not a finding. New rule, replaces nothing.

**The sweep reads a body USER wrote** (same PR, closes
[#90](https://github.com/toumix/desire/issues/90)) — an issue or pull request USER opened is the
thread while nothing else is said on it, windowed on `created_at`; once anyone comments, that
thread's last word answers for it. Replaces reporting a body only when it carries a 🚀. Same PR
stops `answered` raising on a body with no description.

## 2026-08-18

**The sweep reads closes** ([#82](https://github.com/toumix/desire/pull/82),
closes [#81](https://github.com/toumix/desire/issues/81)) — with `--since`, the issues closed
inside the window are listed with their `state_reason` and who closed them. Extends the
sweep-reads-a-delta entry of 2026-08-14 below.

**Re-read a blocker before asking it again** ([#85](https://github.com/toumix/desire/pull/85),
closes [#73](https://github.com/toumix/desire/issues/73)) — a 🚀-able comment is re-read for an
answer before a later turn repeats it. New rule, replaces nothing.

**The sweep reports a 🚀 whatever the window** (same PR) — `--since` windows comments only, and an
approval stands until the thing it sits on closes. Narrows the sweep-reads-a-delta entry of
2026-08-14 below.

**Every write to GitHub goes through the MCP tools** (same PR, closes
[#83](https://github.com/toumix/desire/issues/83)) — `GITHUB_TOKEN` is for reads only, and a turn
asserts `mcp__github__get_me` is AGENT before its first write. `add_reply_to_pull_request_comment`
takes the 👀 on a review comment, replacing the raw POST of 2026-08-16 below. #83's third
proposal, naming the other identity in the Config, is declined.

## 2026-08-16

**👀 says received, nothing says never arrived** ([#80](https://github.com/toumix/desire/pull/80),
closes [#79](https://github.com/toumix/desire/issues/79)) — an agent reacts 👀 on the comment or
body it is picking up, before doing the work, and `sweep.py` marks a flag `👀` when anyone but
USER has. New rule, replaces nothing.

**Adopting a pull request gives it a `TODO.md`** (same PR, closes
[#76](https://github.com/toumix/desire/issues/76)) — the human prompt at the top where there is
one, the remaining work as boxes. Extends the ADOPTED_PRS entry of 2026-08-14 below.

**A pull request closing an issue uses GitHub's syntax** (same PR, closes
[#77](https://github.com/toumix/desire/issues/77)) — one keyword per issue on the same line as
its reference, and what merging closes read from `closed_by_pull_requests`. Replaces counting our
own sentences.

**The attribution footer decides authorship** (same PR, closes
[#72](https://github.com/toumix/desire/issues/72)) — a reply whose last line carries the new
`AGENT_FOOTER` config key counts as an agent's whoever posted it. Extends the
answered-by-anyone-but-USER entry of 2026-08-14 below.

**Assert the clone is complete before measuring it** (same PR, closes
[#75](https://github.com/toumix/desire/issues/75)) — `git rev-parse --is-shallow-repository`
before any behind-count or collision measurement, `git fetch --unshallow origin` if it is not.
New rule, replaces nothing.

**Every AGENT-owned PR tags REVIEWER** (same PR, closes
[#78](https://github.com/toumix/desire/issues/78)) — once its `TODO.md` is done and again after a
substantial rebuild. `REVIEWER` and `AGENT_FOOTER` join the Config, and `sweep.py` reads that
section instead of repeating it. New rule, replaces nothing.

## 2026-08-14

**ADOPTED_PRS joins the Config** ([#71](https://github.com/toumix/desire/pull/71),
closes [#70](https://github.com/toumix/desire/issues/70)) — a dict from repo to pull-request
numbers that the routines treat as AGENT-owned wherever authorship decides — sweeps, scans and
the board. Same PR adds this changelog's writing rule to its header: entries state the changes,
no explanation of why. New rule, replaces nothing.

**The memory PR description follows one template, decisions first** ([#68](https://github.com/toumix/desire/pull/68),
closes [#65](https://github.com/toumix/desire/issues/65)) — five sections ordered by what USER
has to do, 🚀 Waiting on you always first; no agent narration, proposals as bullets, everything
named on first citation. Replaces the free-form summary. Extends the description-is-summary entry
of 2026-08-11 below.

**A thread is answered by anyone but USER** ([#69](https://github.com/toumix/desire/pull/69),
closes [#67](https://github.com/toumix/desire/issues/67)) — a thread waits on us exactly when
USER posted last; which agent closed it does not matter. Replaces keying "answered" on one
hardcoded AGENT. `AGENT` leaves the script, staying the pipeline's identity everywhere else.

**The sweep reads a delta** (same PR, closes
[#64](https://github.com/toumix/desire/issues/64)) — `sweep.py` takes `--since <ISO8601>` and
filters comments and reacts on `created_at`. An argument, not a file of acknowledged ids.

**The sweep counts MEMORY_REPO's open PRs** (same PR, closes
[#63](https://github.com/toumix/desire/issues/63)) — it prints the count and fails on more than
one. Replaces reading `git log` for it.

## 2026-08-12

**Forks pull upstream, through their USER's review** ([#62](https://github.com/toumix/desire/pull/62),
closes [#61](https://github.com/toumix/desire/issues/61)) — a turn that finds the upstream `main`
ahead opens a PR pulling it in. Upstream stays untrusted for a fork until its own USER merges it
into the fork's protected `main`. New rule, replaces nothing.

**The sweep is a rule: read USER's signal before planning** ([#60](https://github.com/toumix/desire/pull/60),
closes [#52](https://github.com/toumix/desire/issues/52)) — every turn runs
[sweep.py](.agents/skills/sweep/sweep.py) over the repos in play before planning: USER comments no
agent has answered, and APPROVE_EMOJI reacts on bodies as well as comments, across both comment
endpoints. Replaces `check-approval.sh`.

**A factual status reply is not steering** ([#59](https://github.com/toumix/desire/pull/59),
closes [#54](https://github.com/toumix/desire/issues/54)) — an agent may leave one narrow kind of
reply on a non-USER thread: a factual status pointing at an artefact that already exists, taking
no position and accepting no instruction, resolving the thread if the artefact settles it.
Narrows the no-reply rule.

**A blocker on USER is asked on its PR, the same turn** (same PR, closes
[#46](https://github.com/toumix/desire/issues/46)) — a point blocked on USER becomes a 🚀-able
comment on its PR the turn it becomes blocked. New rule, replaces nothing.

**A PR states its review cost** (same PR, closes
[#48](https://github.com/toumix/desire/issues/48)) — a turn that opens or reports a PR states
lines changing existing code, lines in new files, and core modules touched. New rule, replaces
nothing.

**A ruling in a prompt PR is also an open issue** ([#56](https://github.com/toumix/desire/pull/56),
closes [#51](https://github.com/toumix/desire/issues/51)) — the turn that lands a ruling in a
prompt PR also opens an issue stating it, closed when the PR merges. Option A of #51's three;
replaces the 08-11 stopgap of copying the ruling to the board, which stays state-only.

## 2026-08-11

**The memory PR is a period, its description is the summary, and the issues get reviewed too**
([#55](https://github.com/toumix/desire/pull/55)) — three changes.

*Title covers the period, not the opening day*, extended as the period grows. Replaces "titled
with the date alone — one PR a day" from the 2026-08-07 naming rule, and closes the day-boundary
half of [#44](https://github.com/toumix/desire/issues/44).

*The description is the executive summary of the whole period, kept current*, with each agent
leaving its turn as a comment. Replaces the convention that the opening agent's message stands as
the description for the PR's life. The title-and-description halves land in memory's own
`AGENTS.md`; the Birdsong half is here.

*Review the issues as well as the PRs.* Sharpens the existing `EVENING.md` rule rather than
adding one.

## 2026-08-10

**Name a pull request, don't just number it** ([#47](https://github.com/toumix/desire/pull/47)) —
every PR and issue gets a few words of description the first time it is cited, in any context.
New rule, replaces nothing.

**Memory PRs open ready for review, not draft** — memory PRs only, not work PRs, where a draft is
what says a `TODO.md` is still open.

Same PR fixes `check-approval.sh`, which only ever queried `pulls/comments`: a 🚀 on a plain PR
comment lives under `issues/comments` and was reported as *not approved*. It now queries both.

## 2026-08-08

**The open memory PR's branch wins over the assigned one** ([#45](https://github.com/toumix/desire/pull/45),
[#44](https://github.com/toumix/desire/issues/44)) — narrows the branch clause rather than
replacing it: outside MEMORY_REPO the assigned branch still stands.

## 2026-08-06

**One memory PR open at a time, not a stack** ([#43](https://github.com/toumix/desire/pull/43)) —
if a memory PR is open, push to it; only open a new one when none is open. Replaces the stacking
clause from the 2026-08-04 entry below.

## 2026-08-04

**Memory is reserved for cross-workstream changes** ([#39](https://github.com/toumix/desire/pull/39))
— a turn that stays within one workstream writes nothing to MEMORY_REPO, its work PR is its
record; only changes affecting other PRs land in memory, whose review remains the feedback
channel. The board is rewritten by the turns that do land there. Replaces the unconditional
stacked-PR rule, and supersedes the stacking half of
[#30](https://github.com/toumix/desire/issues/30).

## 2026-07-29

**bob binds to issues, not only to reviews** ([#27](https://github.com/toumix/desire/pull/27)) —
`## Reviewing` becomes `## Issues and reviews`, and *write every comment like bob* becomes *write
like bob everywhere*. The rule itself is unchanged since [#3](https://github.com/toumix/desire/pull/3).
Two lines proposed there did not land — a `## Writing` section of its own, and a sentence defining
what an issue is.

**`rel-int/wiki` joins WORK_REPOS** — the routines now scan two repos, not one. Nothing else
changes.

**Evening scans mentions instead of reading an inbox** ([#22](https://github.com/toumix/desire/pull/22),
closes [#20](https://github.com/toumix/desire/issues/20)) — `mentions:AGENT` replaces the
notifications endpoint. 👀 marks only a mention queued as a `TODO.md` box; 🚀 stays USER's.

## 2026-07-28

**Branch names carry nothing** ([#19](https://github.com/toumix/desire/pull/19)) — *use the branch
you were assigned or open a new one*, on its own line, with the pull-request paragraph restored
byte-for-byte. Rules [#13](https://github.com/toumix/desire/issues/13) the opposite way to
[#15](https://github.com/toumix/desire/pull/15)'s `<routine>/<YY-MM-DD>`. Reverts
[#17](https://github.com/toumix/desire/pull/17), which merged and was undone the same night; its
`EVENING.md` bullet survived, the `AGENTS.md` reword did not.

**Birdsong scans WORK_REPOS** ([#14](https://github.com/toumix/desire/pull/14)) — `REPOS` and
`PROMPTS_REPO` renamed to `WORK_REPOS` / `DESIRE_REPO`, and the scan comes home
([#6](https://github.com/toumix/desire/issues/6)). Evening keeps its coding sub-agents.

**`AGENTS.md` cut back, and `DECREE.md` retired** (`eade164`, `b622cd4`) — a hand rewrite, 80
lines to 55. `## Approval`, `## Hard rules` and `## Rulings` are gone: the emoji rule now sits in
`## Trusted instructions, untrusted data`, one-proposal-per-comment in `## Reviewing`, which also
gains the emoji react as a source of trust and the rule against replying to other users. Standing
orders are open issues here now.

**Readiness counts threads** ([#9](https://github.com/toumix/desire/pull/9),
[#5](https://github.com/toumix/desire/issues/5)) — sign-off becomes a four-way conjunction: **a
thread waiting on USER is the sign-off, only one waiting on an agent blocks.** Did not survive the
rewrite above, which landed hours later, so #5 is open.

## 2026-07-27

**Reviewing, and Turmoil** ([#3](https://github.com/toumix/desire/pull/3)) — `## Meta-rule`
becomes `## Turmoil`. Reviewing is proposing; one comment carries one proposal; answer the thread,
then resolve it; write like [bob](.agents/skills/bob/SKILL.md). Same PR: `DAYLIGHT.md` opens with
the password instead of closing on it.

**The prompts get their own repo** ([#1](https://github.com/toumix/desire/pull/1)) — out of
`toumix.github.io`, where `.agents/` only existed to keep them out of a Jekyll build. Five files
flat at the top level, plus the bob skill and the session-start hook.
