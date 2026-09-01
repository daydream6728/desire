# The memory

This private repo is the MEMORY_REPO of the routines named for the three phases of a turn — 🐦
Birdsong, 🌤️ Daylight, 🌙 Evening. The rules they follow are public and live in DESIRE_REPO; this
is the work, so it stays here. [`config.env`](config.env) at the root is the one file that names
USER, AGENT and the repos, and both the prompts and the tooling read it from here.

Five kinds of file, each with exactly **one lifetime**:

- [`WORK/<repo>/<number>.md`](WORK) — one standing note per open pull request, **rewritten by
  whichever session touches that head**, deleted by the turn that sees it merged or closed. Every
  session writes the file of every head it touched, even when the work never left that pull
  request: it is how an interactive turn is visible to the next morning's plan. Shape in
  [`WORK/TEMPLATE.md`](WORK/TEMPLATE.md).
- [`README.md`](README.md) — the board, **rewritten every turn**: cross-cutting state only. What
  collides with what, what merge order is forced, what has been ruled. A fact about one head goes
  in that head's own file. **It stays under 200 lines**: a turn that would push it over drops the
  oldest section rather than appending, and `wc -l README.md` says whether it is over before the
  push.
- [`TURNS/<date>.md`](TURNS) — the turn journal, **write-once**: one section per routine, in firing
  order, carrying what changed rather than the whole picture. Shape in
  [`TURNS/TEMPLATE.md`](TURNS/TEMPLATE.md).
- [`USER_TODO.md`](USER_TODO.md) — USER's own list, as checkboxes: what only USER can do under
  **Yours**, then what waits on USER — one react, one merge or one word each — grouped by whose
  work it unblocks. A turn ticks a box only on evidence, never one under **Yours**, and drops the
  line on the next rewrite.
- [`OTHERS/<person>.md`](OTHERS) — one standing note per collaborator, **rewritten when
  re-read**, not per turn. Shape in [`OTHERS/TEMPLATE.md`](OTHERS/TEMPLATE.md).

One pull request per day, titled with that day, shared by all three routines — a routine name in
the title is wrong. Its **description is the day's executive summary and 🐦 Birdsong alone writes
it**, to the shape in [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md); every
routine leaves a comment for its own turn. That PR's review is USER's feedback channel and its
comment thread is the short-term memory — verbatim quotes with their context, discarded when the PR
merges, so anything meant to outlive it goes in the description, a file, or an issue.

**Standing orders are open issues on DESIRE_REPO**, not a file here. A ruling that outlives the
pull request it was made on belongs in the prompts; until a prompt file carries it, it waits as an
open issue there, where USER can see it and close it. Read those open issues before planning
anything — re-deriving a ruling from scratch is how a wrong one survives.
