# Changelog

What landed on `main`, newest first — when each rule started binding, and what it replaced.
Entries state the changes, no explanation of why.

## 2026-08-16

**👀 says received, nothing says never arrived** ([#PR](https://github.com/toumix/desire/pull/PR),
closes [#79](https://github.com/toumix/desire/issues/79)) — an agent reacts 👀 on the comment or
body it is picking up, before doing the work, and `sweep.py` marks a flag `👀` when anyone but
USER has. A flag on its own could not tell work in progress from an instruction that never
reached a turn. New rule, replaces nothing.

**Adopting a pull request gives it a `TODO.md`** (same PR, closes
[#76](https://github.com/toumix/desire/issues/76)) — the human prompt at the top where there is
one, the remaining work as boxes. Four of the ten adopted PRs predate rule 1 and carry none, and
discopy's guard marks a PR ready only when a push *deletes* one, so
[#347](https://github.com/discopy/discopy/pull/347) met all three sign-off criteria and could not
leave draft by any push. Extends the ADOPTED_PRS entry of 2026-08-14 below.

**A pull request closing an issue uses GitHub's syntax** (same PR, closes
[#77](https://github.com/toumix/desire/issues/77)) — one keyword per issue on the same line as
its reference, and what merging closes read from `closed_by_pull_requests`. Eight queued PRs
carried no keyword at all, `closes #1, #2` linked the first only, and a line break between
keyword and number linked neither; three boards recorded
[#437](https://github.com/discopy/discopy/issues/437) as closed by
[#438](https://github.com/discopy/discopy/pull/438) while GitHub left it open. Replaces counting
our own sentences.

**The attribution footer decides authorship** (same PR, closes
[#72](https://github.com/toumix/desire/issues/72)) — a reply whose last line carries the Claude
Code link counts as an agent's whoever posted it. The adopted PRs predate the agent handle and
were answered from USER's own account: sixteen threads on
[#399](https://github.com/discopy/discopy/pull/399) came back as unanswered USER signal every
night. Extends the answered-by-anyone-but-USER entry of 2026-08-14 below.

**Assert the clone is complete before measuring it** (same PR, closes
[#75](https://github.com/toumix/desire/issues/75)) — `git rev-parse --is-shallow-repository`
before any behind-count or collision measurement. Shallow, `git merge-base` exits 1 and
`git merge-tree` dies with exit 128 and no `CONFLICT` line, which reads as no conflicts: a turn
reported two branches as having no common ancestor and needing a rebuild, when one was 19
conflicts behind and the other 1. New rule, replaces nothing.

**Every AGENT-owned PR tags `@cubic-dev-ai`** (same PR, closes
[#78](https://github.com/toumix/desire/issues/78)) — on open and after a substantial rebuild; its
review is answered like anyone else's. New rule, replaces nothing; supersedes for now the bespoke
reviewer-agent design of 08-14.

## 2026-08-14

**ADOPTED_PRS joins the Config** ([#71](https://github.com/toumix/desire/pull/71),
closes [#70](https://github.com/toumix/desire/issues/70)) — a dict from repo to pull-request
numbers that the routines treat as AGENT-owned wherever authorship decides — sweeps, scans and
the board. Same PR adds this changelog's writing rule to its header: entries state the changes,
no explanation of why. New rule, replaces nothing.

**The memory PR description follows one template, decisions first** ([#68](https://github.com/toumix/desire/pull/68),
closes [#65](https://github.com/toumix/desire/issues/65)) — five sections ordered by what USER
has to do, 🚀 Waiting on you always first; no agent narration, proposals as bullets, everything
named on first citation. Replaces the free-form summary, which led with pipeline state and buried
the one actionable section last. Landed in memory's `AGENTS.md` first, moved here a day later:
conventions are rules, rules are public prompts reviewed by PR, and the fork-pull rule only ships
what desire carries. Extends the description-is-summary entry of 2026-08-11 below.

**A thread is answered by anyone but USER** ([#69](https://github.com/toumix/desire/pull/69),
closes [#67](https://github.com/toumix/desire/issues/67)) — `sweep.py` keyed "answered" on one hardcoded AGENT, so every thread another agent replied to came
back as unanswered USER signal: 18 of the 59 review-comment flags on `discopy/discopy`, including
all five threads on [#514](https://github.com/discopy/discopy/pull/514), which
`giodefelice-agents` answered and resolved within fifteen minutes on 08-04 and which had been
reported every night since. Now a thread waits on us exactly when USER posted last; which agent
closed it does not matter. `AGENT` leaves the script — it is still the pipeline's identity, just
not the sweep's notion of an answer.

**The sweep reads a delta** (same PR, closes
[#64](https://github.com/toumix/desire/issues/64)) — `sweep.py` takes
`--since <ISO8601>` and filters comments and reacts on `created_at`. A 🚀 has no answered state, so
without a window an approval acted on days ago is flagged forever — one had been reported four
nights running — and 84 lines of known noise is where a real signal gets skimmed past, which is
what [#52](https://github.com/toumix/desire/issues/52) was filed to prevent. An argument, not a
file of acknowledged ids: the sweep's whole value is reading GitHub instead of our own notes, and a
`--since` gap is visible and recoverable where a stale file is neither.

**The sweep counts MEMORY_REPO's open PRs** (same PR, closes
[#63](https://github.com/toumix/desire/issues/63)) — two memory PRs were open
at once because `git log` showed our own last one merged, which says nothing about one another turn
opened — [#52](https://github.com/toumix/desire/issues/52)'s shape again, reading state we wrote
ourselves. The sweep already walks every open PR, so it now prints the count and fails on more than
one. Checked by the thing that already runs, rather than by an agent remembering to look.

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
`check-approval.sh`: its one question — did USER 🚀 this
comment? — is the sweep run on that comment's PR or issue, read off one line of output.

**A factual status reply is not steering** ([#59](https://github.com/toumix/desire/pull/59),
closes [#54](https://github.com/toumix/desire/issues/54)) — the no-reply rule keeps its teeth for anything that changes what we build, but an agent may leave
one narrow kind of reply on a non-USER thread — a factual status pointing at an artefact that
already exists, taking no position and accepting no instruction, resolving the thread too if the
artefact settles it. Ends the archaeology of telling "unanswered because ignored" from
"unanswered because rule 4": daydream6728's three threads were acted on within minutes and could
never say so.

**A blocker on USER is asked on its PR, the same turn** (same PR, closes
[#46](https://github.com/toumix/desire/issues/46)) — a point blocked on USER becomes a 🚀-able comment on its PR the turn it becomes blocked; a blocker
recorded only in a `TODO.md` or on the board has not been asked. Three blockers sat for days —
one for two weeks — in places USER never reads, each re-derived from scratch by a later turn.

**A PR states its review cost** (same PR, closes
[#48](https://github.com/toumix/desire/issues/48)) — review minutes are the
bottleneck, so a turn that opens or reports a PR states lines changing existing code, lines in new
files, and core modules touched. The split matters more than the total: a 234-line new module is a
cheaper read than an 80-line fix to `closed.py`.

**A ruling in a prompt PR is also an open issue** ([#56](https://github.com/toumix/desire/pull/56),
closes [#51](https://github.com/toumix/desire/issues/51)) — a ruling
lived only in a memory PR's thread and the unmerged [#47](https://github.com/toumix/desire/pull/47);
the thread merged away and the ruling went invisible for a day. Now the turn that lands a ruling in a
prompt PR also opens an issue stating it, closed when the PR merges — an open issue is what
AGENTS.md already tells every planner to read. Option A of #51's three; option B, copying the
ruling to the board, was the 08-11 stopgap this replaces, and the board stays state-only.

## 2026-08-11

**The memory PR is a period, its description is the summary, and the issues get reviewed too**
([#55](https://github.com/toumix/desire/pull/55)) — three changes.

*Title covers the period, not the opening day.* Replaces "titled with the date alone — one PR a
day" from the 2026-08-07 naming rule: a memory PR routinely outlives the date it was opened on,
and the title is extended rather than left stale. This also **closes the day-boundary half of
[#44](https://github.com/toumix/desire/issues/44)** — a PR spanning a day boundary was the anomaly
that question was about, and it is now the normal case.

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
every PR and issue gets a few words of description the first time it is cited, in any context —
USER does not know the numbers by heart. Applies everywhere, not just to comments: the board and
the turn files were the worst offenders, being almost entirely numbers. New rule, replaces nothing.

**Memory PRs open ready for review, not draft** — so merging is one click, not two. Memory PRs
only, not work PRs: on discopy a draft is what says a `TODO.md` is still open.

Same PR fixes `check-approval.sh`, which only ever queried `pulls/comments`, i.e. review comments
attached to a line of the diff. A 🚀 on a plain PR comment lives under `issues/comments` and the
script reported it as *not approved* — which is what it did to the reaction unblocking the Kleisli
trace ([discopy#443](https://github.com/discopy/discopy/pull/443)), found by reading the reaction
count off the comment listing instead. It now queries both.

## 2026-08-08

**The open memory PR's branch wins over the assigned one** ([#45](https://github.com/toumix/desire/pull/45)) —
the branch is whatever the open PR uses ([#44](https://github.com/toumix/desire/issues/44)). The scheduler hands each routine a fresh memory branch every fire, so
"use the branch you were assigned" and "push to the open PR" could not both be obeyed once a PR was
open — the second pileup in two days traceable to the branch convention. Narrows the branch clause
rather than replacing it: outside MEMORY_REPO the assigned branch still stands. The day-boundary
half of #44 — a PR titled with yesterday's date, still the only one open today — stays open.

## 2026-08-06

**One memory PR open at a time, not a stack** ([#43](https://github.com/toumix/desire/pull/43)) —
six memory PRs piling up faster than one human reviews them.
*Stacked on the previous open PR* required every turn to correctly find and target that one PR; four
of five turns didn't, branching off `main` instead, and even a correct stack is still N PRs to open,
review in order and merge. Replaces the stacking clause from the 2026-08-04 entry below: now, if a
memory PR is open, push to it; only open a new one when none is open.

## 2026-08-04

**Memory is reserved for cross-workstream changes** ([#39](https://github.com/toumix/desire/pull/39)) — a turn that stays within one workstream
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
rule and outside it. Two lines proposed here did not land — a `## Writing` section
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
