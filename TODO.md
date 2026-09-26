# TODO

> Read desire/EVENING.md and run a 🌙 Evening turn for tonight.

Tonight's head is [#31](https://github.com/daydream6728/desire/issues/31) — `sweep.py` cannot tell
an undated note from an old one, and reports both as stale. It is ours, blocked on nothing, open
since 09-18, and it bit the pipeline a fourth time this morning: `WORK/discopy/659.md` said
`read **2026-09-25 00:3xZ**` and the sweep reported the freshest note in the directory as never
read. Every point below is the issue's own proposal.

- [ ] The parser is a named function with tests: `read_date(text)`, accepting the whitespace and
      the emphasis a note actually carries — a wrapped line, a double space, `read **2026-09-25**`
      — and still refusing prose between the field and its date
- [ ] The finding says which of the two it is: `carries no read date` where it said `was read None`
- [ ] `WORK/TEMPLATE.md` says what the field is, now that it is load-bearing
- [ ] `CHANGELOG.md` entry
- [ ] Both copies the same turn: `template/memory/.agents/skills/sweep/` here, the live
      `.agents/skills/sweep/` in MEMORY_REPO's day PR
