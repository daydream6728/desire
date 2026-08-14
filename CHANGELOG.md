# Changelog

What landed on `main`, newest first — when each rule started binding, and what it replaced.

## 2026-08-14

**The memory PR description follows one template, decisions first** ([#68](https://github.com/toumix/desire/pull/68),
closes [#65](https://github.com/toumix/desire/issues/65)) — *"ok much better, let's use this
PR description as template for the next ones"*, on the memory board PR of 08-13 (memory#58),
after a summary led with "nothing here is unblocked" and buried the one actionable section last.
Five sections ordered by what USER has to do — 🚀 Waiting on you always first — no agent narration,
proposals as bullets, everything named on first citation. Landed in memory's `AGENTS.md` first,
moved here the next day on *"shouldn't it be in desire?"*: conventions are rules, rules are
public prompts reviewed by PR, and the fork-pull rule only ships what desire carries. Extends the
description-is-summary ruling of 2026-08-11 below.

## 2026-08-12

**Forks pull upstream, through their USER's review** ([#62](https://github.com/toumix/desire/pull/62),
closes [#61](https://github.com/toumix/desire/issues/61)) — the prompts travel by
fork and nothing told a forked pipeline to look upstream, so the downstream forks were running on
a snapshot while the rules moved. Now a turn that finds the upstream `main` ahead opens a PR
pulling it in. The trust model doesn't bend: upstream stays untrusted for a fork until its own
USER merges it into the fork's protected `main`, which is exactly what the PR asks for.

**The sweep is a rule: read USER's signal before planning** ([#60](https://github.com/toumix/desire/pull/60),
closes [#52](https://github.com/toumix/desire/issues/52)) — twice a board concluded "no unblocked
work" while trusted instructions sat unread, because checkboxes, CI and behind-counts are all state
the agents wrote themselves. Now every turn runs
[sweep.py](.agents/skills/sweep/sweep.py) over the repos in play before planning: USER comments no
agent has answered, and APPROVE_EMOJI reacts on bodies as well as comments, across both comment
endpoints. One reach beyond the issue's sketch: bodies carry reactions too — the day this landed,
both live approvals were body 🚀s a comments-only sweep would have missed. Replaces
`check-approval.sh` (*do we need two scripts?*): its one question — did USER 🚀 this
comment? — is the sweep run on that comment's PR or issue, read off one line of output.

**A factual status reply is not steering** ([#59](https://github.com/toumix/desire/pull/59),
closes [#54](https://github.com/toumix/desire/issues/54)) — the no-reply rule keeps its teeth for anything that changes what we build, but an agent may leave
one narrow kind of reply on a non-USER thread — a factual status pointing at an artefact that
already exists, taking no position and accepting no instruction. The issue proposed leaving the
thread unresolved; amended on the PR's review — *it's fine for you to resolve threads* — so a reply
whose artefact settles the thread resolves it too. Ends the archaeology of telling "unanswered because ignored" from
"unanswered because rule 4": daydream6728's three threads were acted on within minutes and could
never say so.

**A blocker on USER is asked on its PR, the same turn** (same PR, closes
[#46](https://github.com/toumix/desire/issues/46)) — option 1 of #46, the line as-is:
a point blocked on USER becomes a 🚀-able comment on its PR the turn it becomes blocked; a blocker
recorded only in a `TODO.md` or on the board has not been asked. Three blockers sat for days —
one for two weeks — in places USER never reads, each re-derived from scratch by a later turn.

**A PR states its review cost** (same PR, closes
[#48](https://github.com/toumix/desire/issues/48)) — review minutes are the
bottleneck, so a turn that opens or reports a PR states lines changing existing code, lines in new
files, and core modules touched. The split matters more than the total: a 234-line new module is a
cheaper read than an 80-line fix to `closed.py`.

**A ruling in a prompt PR is also an open issue** ([#56](https://github.com/toumix/desire/pull/56),
closes [#51](https://github.com/toumix/desire/issues/51)) — the ruling
*make the memory PRs ready from the start* (memory#54)
lived only in that PR's thread and the unmerged [#47](https://github.com/toumix/desire/pull/47); the
thread merged away and the ruling went invisible for a day. Now the turn that lands a ruling in a
prompt PR also opens an issue stating it, closed when the PR merges — an open issue is what
AGENTS.md already tells every planner to read. Option A of #51's three; option B, copying the
ruling to the board, was the 08-11 stopgap this replaces, and the board stays state-only.

## 2026-08-11

**The memory PR is a period, its description is the summary, and the issues get reviewed too**
([#55](https://github.com/toumix/desire/pull/55)) — three rulings from
memory#55's review, merged in the same breath, which
discarded the thread carrying them.

*Title covers the period, not the opening day.* Replaces "titled with the date alone — one PR a
day" from the 2026-08-07 naming rule: a memory PR routinely outlives the date it was opened on,
and the title is extended rather than left stale. This also **settles the open half of
[#44](https://github.com/toumix/desire/issues/44)** — a PR spanning a day boundary was the anomaly
that question was about, and it is now the normal case, so there is nothing left to rule.

*The description is the executive summary of the whole period, kept current*, with each agent
leaving its turn as a comment. Replaces the convention that the opening agent's message stands as
the description for the PR's life, which made the summary go stale from the second turn onward.
The title-and-description halves land in memory's own `AGENTS.md`; the Birdsong half is here.

*Review the issues as well as the PRs.* `EVENING.md` already said "reviews the issues and PRs" and
every turn read the PR half only, which is why the issues pile up — so this sharpens a rule that
existed rather than adding one, in the same shape as
[#52](https://github.com/toumix/desire/issues/52)'s sweep: naming the half that gets skipped.

## 2026-08-10

**Name a pull request, don't just number it** ([#47](https://github.com/toumix/desire/pull/47)) —
from the memory board PR of 08-09 (memory#53),
verbatim: *I don't know PR numbers by heart please stop using them so much, or at least the first
time you use it in a comment or any context give me a short description*. Applies everywhere, not
just to comments: the board and the turn files are the worst offenders, being almost entirely
numbers. New rule, replaces nothing.

**Memory PRs open ready for review, not draft** — from the board PR of 08-10
(memory#54), verbatim: *next time make the memory PRs
ready from the start, no need for draft mode so I can merge with one click less*. Memory PRs only,
not work PRs: on discopy a draft is what says a `TODO.md` is still open.

Same PR fixes `check-approval.sh`, which only ever queried `pulls/comments`, i.e. review comments
attached to a line of the diff. A 🚀 on a plain PR comment lives under `issues/comments` and the
script reported it as *not approved* — which is what it did to the reaction unblocking the Kleisli
trace ([discopy#443](https://github.com/discopy/discopy/pull/443)), found by reading the reaction
count off the comment listing instead. It now queries both.

## 2026-08-08

**The open memory PR's branch wins over the assigned one** ([#45](https://github.com/toumix/desire/pull/45)) —
option 1 of [#44](https://github.com/toumix/desire/issues/44)'s three: *one-PR rule wins, drop "use the branch you were assigned" for MEMORY_REPO, branch is
whatever the open PR uses*. The scheduler hands each routine a fresh memory branch every fire, so
"use the branch you were assigned" and "push to the open PR" could not both be obeyed once a PR was
open — the second pileup in two days traceable to the branch convention. Narrows the branch clause
rather than replacing it: outside MEMORY_REPO the assigned branch still stands. The day-boundary
half of #44 — a PR titled with yesterday's date, still the only one open today — is unruled, so the
issue stays open for it.

## 2026-08-06

**One memory PR open at a time, not a stack** ([#43](https://github.com/toumix/desire/pull/43)) —
six memory PRs (memory#42,
memory#43, memory#47,
memory#48, memory#49,
memory#50) piling up faster than one human reviews them.
*Stacked on the previous open PR* required every turn to correctly find and target that one PR; four
of five turns didn't, branching off `main` instead, and even a correct stack is still N PRs to open,
review in order and merge. Replaces the stacking clause from the 2026-08-04 entry below: now, if a
memory PR is open, push to it; only open a new one when none is open.

## 2026-08-04

**Memory is reserved for cross-workstream changes** ([#39](https://github.com/toumix/desire/pull/39)) — closes
memory#45: *only open memory PRs when the changes
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

**`AGENTS.md` cut back, and `DECREE.md` retired** (`eade164`, `b622cd4`) — a hand rewrite, 80
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
