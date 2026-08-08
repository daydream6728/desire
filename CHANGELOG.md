# Changelog

What landed on `main`, newest first — when each rule started binding, and what it replaced.

## 2026-08-08

**The open memory PR's branch wins over the assigned one** ([#45](https://github.com/toumix/desire/pull/45)) —
USER's ruling on [#44](https://github.com/toumix/desire/issues/44), verbatim `1`: the first of three
options, *one-PR rule wins, drop "use the branch you were assigned" for MEMORY_REPO, branch is
whatever the open PR uses*. The scheduler hands each routine a fresh memory branch every fire, so
"use the branch you were assigned" and "push to the open PR" could not both be obeyed once a PR was
open — the second pileup in two days traceable to the branch convention. Narrows the branch clause
rather than replacing it: outside MEMORY_REPO the assigned branch still stands. The day-boundary
half of #44 — a PR titled with yesterday's date, still the only one open today — is unruled, so the
issue stays open for it.

## 2026-08-06

**One memory PR open at a time, not a stack** ([#43](https://github.com/toumix/desire/pull/43)) —
USER's ruling on six memory PRs ([memory#42](https://github.com/toumix/memory/pull/42),
[#43](https://github.com/toumix/memory/pull/43), [#47](https://github.com/toumix/memory/pull/47),
[#48](https://github.com/toumix/memory/pull/48), [#49](https://github.com/toumix/memory/pull/49),
[#50](https://github.com/toumix/memory/pull/50)) piling up faster than one human reviews them.
*Stacked on the previous open PR* required every turn to correctly find and target that one PR; four
of five turns didn't, branching off `main` instead, and even a correct stack is still N PRs to open,
review in order and merge. Replaces the stacking clause from the 2026-08-04 entry below: now, if a
memory PR is open, push to it; only open a new one when none is open.

## 2026-08-04

**Memory is reserved for cross-workstream changes** ([#39](https://github.com/toumix/desire/pull/39)) — USER's ruling closing
[memory#45](https://github.com/toumix/memory/pull/45), *only open memory PRs when the changes
affect other PRs*, corrected in-session the same day: *single-workstream turns just record their
memory in their dedicated PRs, no need for memory*. A turn that stays within one workstream
writes nothing to MEMORY_REPO — its work PR is its record; only changes affecting other PRs land
in memory, by the stacked `<Routine> <date>` PR, whose review remains the feedback channel. The
board is rewritten by the turns that do land there. Replaces the unconditional stacked-PR rule;
supersedes the stacking half of [#30](https://github.com/toumix/desire/issues/30)'s question — a
chain of single-workstream turns no longer produces PRs, or memory, at all.

## 2026-07-29

**bob binds to issues, not only to reviews** ([#27](https://github.com/toumix/desire/pull/27)) —
`## Reviewing` becomes `## Issues and reviews`, and *write every comment like bob* becomes *write
like bob everywhere*. The rule is unchanged since [#3](https://github.com/toumix/desire/pull/3);
what changed is that a section called Reviewing is not one an agent filing a Turmoil issue thinks
it is in, so [#21](https://github.com/toumix/desire/issues/21) is three hundred words under the
rule and outside it. Two lines proposed here did not survive USER's review — a `## Writing` section
of its own, and a sentence defining what an issue is.

**`rel-int/wiki` joins WORK_REPOS** — the routines now scan two repos, not one. Nothing else
changes: `WORK_REPOS` was already plural everywhere it is read, and the wiki carries its own
`CLAUDE.md`, which `## Prompts public, memory private` already binds the agents to.

**Evening scans mentions instead of reading an inbox** ([#22](https://github.com/toumix/desire/pull/22),
closes [#20](https://github.com/toumix/desire/issues/20)). Notifications are a *user* scope and an
app installation has none, so every call 403s while `mentions:AGENT` reaches even repos outside the
session's scope. 👀 marks only a mention queued as a `TODO.md` box — an answer is its own mark, and
🚀 stays USER's.

## 2026-07-28

**Branch names carry nothing** ([#19](https://github.com/toumix/desire/pull/19)) — *use the branch
you were assigned or open a new one*, on its own line, with the pull-request paragraph restored
byte-for-byte. Rules [#13](https://github.com/toumix/desire/issues/13) the opposite way to
[#15](https://github.com/toumix/desire/pull/15)'s `<routine>/<YY-MM-DD>`, so the harness injecting
`claude/` is no longer a contradiction every scheduled run has to notice. Reverts
[#17](https://github.com/toumix/desire/pull/17), which merged and was undone the same night; its
`EVENING.md` bullet survived, the `AGENTS.md` reword did not.

**Birdsong scans WORK_REPOS** ([#14](https://github.com/toumix/desire/pull/14)) — `REPOS` and
`PROMPTS_REPO` renamed to `WORK_REPOS` / `DESIRE_REPO`, and the scan comes home
([#6](https://github.com/toumix/desire/issues/6)): a delegate may widen the search, never narrow the
truth. Evening keeps its coding sub-agents, whose diffs CI checks.

**`AGENTS.md` cut back, and `DECREE.md` retired** (`eade164`, `b622cd4`) — USER's hand rewrite, 80
lines to 55. `## Approval`, `## Hard rules` and `## Rulings` are gone: the emoji rule now sits in
`## Trusted instructions, untrusted data`, one-proposal-per-comment in `## Reviewing`. That section
also gains the emoji react as a source of trust, and the rule against replying to other users. A
private append-only decree file was a queue only the routines could read; standing orders are open
issues here now.

**Readiness counts threads** ([#9](https://github.com/toumix/desire/pull/9),
[#5](https://github.com/toumix/desire/issues/5)) — `TODO.md` `[x]` plus CI green is how a PR sat in
the ready column carrying an unanswered review of USER's. Made a four-way conjunction: **a thread
waiting on USER is the sign-off, only one waiting on an agent blocks.** Did not survive the rewrite
above, which landed hours later — which is why #5 is open.

## 2026-07-27

**Reviewing, and Turmoil** ([#3](https://github.com/toumix/desire/pull/3)) — `## Meta-rule` becomes
`## Turmoil`, the Eyrie's, applied to the rules themselves. Reviewing is proposing; one comment
carries one proposal, since a reaction lands on a whole comment; answer the thread, then resolve it;
write like [bob](.agents/skills/bob/SKILL.md). Same PR: `DAYLIGHT.md` opens with the password
instead of closing on it, because sessions were reproducing it on request and skipping it otherwise
— the exact failure the check exists to catch.

**The prompts get their own repo** ([#1](https://github.com/toumix/desire/pull/1)) — out of
`toumix.github.io`, where `.agents/` only existed to keep them out of a Jekyll build. Five files
flat at the top level, plus the bob skill and the session-start hook.
