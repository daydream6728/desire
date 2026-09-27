# TODO

> Read desire/EVENING.md and run a 🌙 Evening turn for tonight.

Tonight's head is [#32](https://github.com/daydream6728/desire/issues/32) — nothing compares a
head's green to its base's tip, so a stale pass reads as sign-off condition 2. It is ours, it
blocks nothing, and it is the dangerous one of the pair: where
[#31](https://github.com/daydream6728/desire/issues/31) over-reports staleness, this under-reports
it, so the failure mode is asking USER to merge something CI never validated. Filed 09-19,
weighed against #31 last night and deliberately not taken; the issue's own proposals 1 and 2 are
"ours and small", and its proposal 3 is a rule and stays USER's.

- [ ] Proposal 1, the arithmetic: on every AGENT-owned head, compare the newest check run against
      the tip of the head's **own** base ref — `split/3`, not `main` — and report a green that
      cannot have seen it. A head with no check run at all is context, not a finding: desire runs
      no CI
- [ ] Proposal 2, the base tip in the note: `WORK/TEMPLATE.md`'s **state** line carries the base
      ref and the sha the checks ran against, `sweep.py` reads it and names it beside the live tip.
      A note carrying none is silent — 103 notes predate the field
- [ ] Tests for both, pure where the arithmetic is
- [ ] `OPERATIONS.md` says what the finding means and what it costs
- [ ] `CHANGELOG.md` entry
- [ ] Both copies the same turn: `template/memory/.agents/skills/sweep/` here, the live
      `.agents/skills/sweep/` in MEMORY_REPO's day PR
- [ ] Proposal 3 is **not** taken: it is a rule, and rules go to USER
