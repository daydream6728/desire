# TODO

USER, live session 2026-09-01, verbatim:

> Help me scan through desire issues and PRs so we can ship a refreshed version after Codex gave
> some feedback to diagnose why Evening and Birdsong are rather useless
>
> Another point I thought about: every daylight session should in fact make a summary of its work
> in the memory repo even though the work is purely contained in the corresponding PR, so that
> Birdsong can get a big picture of what's going on
>
> This could go into one markdown file for each PR, which would also replace the stale queue of the
> memory repo's README
>
> Another point: let's make sure desire is completely separate from me (there's a PR to move config
> to memory as it should have from the start) and easy to reproduce for somebody else, in
> particular, there needs to be a template for the memory folder and the memory PRs that a fresh
> clone can use as seed

Four rulings from the same session, in answer to the design questions:

> **Codex #129**: keep finish-first, drop receipts.
> **Per-PR files**: `PRS/<repo>/<n>.md`, the queue dies.
> **Reproducibility**: a `template/` directory in desire.
> **This session**: *"wait what? Daylight definitely should implement, it's been implementing for
> months, let's update the prompt if that's what it says"*

- [x] `DAYLIGHT.md`: Daylight implements — strike "it designs and queues, never implements"
- [x] `DAYLIGHT.md`: every session writes the `PRS/` file of every head it touched, always
- [x] `EVENING.md`: one head to a terminal handoff before selecting another; support work is not an
      outcome; enumerate the expected checks before calling CI green
- [x] `BIRDSONG.md`: read `PRS/` rather than re-derive the queue; the board is cross-cutting only
- [x] `AGENTS.md`: `PRS/<repo>/<number>.md` as the fifth kind of memory file, with its lifetime,
      its shape, and the reversal of "a turn within one workstream leaves MEMORY_REPO untouched"
- [x] `AGENTS.md`: the memory PR template's `Detail` line points at `PRS/`
- [x] `template/`: the seed of a fresh MEMORY_REPO — `AGENTS.md`, `README.md`, `USER_TODO.md`,
      `config.env`, `PRS/TEMPLATE.md`, `REVIEWS/TEMPLATE.md`, `TURNS/TEMPLATE.md` and the day-PR
      body template
- [x] `README.md`: Get started says three repos, where the config lives, and how to seed the memory
- [x] `sweep.py`: exit 2 when a GitHub read fails, and check `PRS/` against the live open-PR list —
      a missing file and an orphan file are both findings
- [x] `CHANGELOG.md` entry
- [ ] Park the rulings as an issue on DESIRE_REPO, closed by this PR
- [ ] Answer Codex on #129 with what survived and what did not; answer #124 and #128
- [x] The companion memory PR: `AGENTS.md`, the board without its queue, and `PRS/` seeded from the
      34 owned heads plus wiki#13
