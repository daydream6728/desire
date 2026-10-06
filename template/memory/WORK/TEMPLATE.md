# `WORK/<repo>/<number>.md`

One file per open pull request, named by the repository and the number: `WORK/discopy/489.md`.
Whichever session touches the head rewrites it before the session ends — 🌤️ Daylight included,
even when the work never leaves that one pull request. The turn that sees it merged or closed
deletes the file.

Five fields, then a log newest-first, one line per turn. Nothing else. If a field has no answer
today, say so — an empty **needs** is a claim that nothing is blocking it, and the next turn will
read it as one.

```markdown
# <repo>#<number> — <what it is, in half a line>

- **state** <draft|ready|merged|closed> · <mergeable_state> · `TODO.md` <n open|all `[x]`|gone|never> ·
  <added>/<removed> lines across <n> files · <n> behind `<base ref>` · base <sha> · read <date>
- **does** one or two lines. The mathematics before the plumbing
- **needs** the one thing that would move it: a read, a ruling, a merge, a fix — and from whom
- **touches** the modules it changes, and the heads it collides with over which files
- **blocks** what waits on it, and what it waits on

- **<date> <phase or person>** what changed, in one line
- **<date> <phase or person>** what changed, in one line
```

An example, so the density is not a guess:

```markdown
# discopy#489 — let statements and non-strictly-associative products in closed terms

- **state** ready · `blocked` · `TODO.md` gone · 2,113/188 across 21 files · 0 behind `main` ·
  base 4d96025 · read 2026-09-01
- **does** adds `let` to the internal language of closed categories, and drops the assumption that
  the product is strictly associative, so a term can name an intermediate value
- **needs** USER's read. Nothing is waiting on an agent
- **touches** `closed.py`, `biclosed.py`, `test/closed.py` — collides with #442 and #511 on `closed.py`
- **blocks** #443's last box, which wants the `trace(0)` fix this carries

- **2026-09-01 🌙 Evening** resolved 19 review threads — 8 fixed, #693 and #694 filed for two,
  4 design questions left for a human — full suite green, deleted `TODO.md`
- **2026-08-27 🌤️ Daylight** designed the `let` encoding with USER, wrote the `TODO.md`
```

**Every live fact carries the date it was read.** State, mergeable state and check results are
cheap to re-read and expensive to be wrong about, so a line that is three days old should read as
three days old rather than as true. A turn that re-reads them updates the date; a turn that does
not, leaves it.

**`read <date>` is a field, not prose**, because `sweep.py` parses it: it reads the first `read`
in the file followed by an ISO date, through any whitespace — a wrapped line included — and through
any emphasis, so `read **2026-09-25 00:3xZ**` is the same field as `read 2026-09-18`. Anything
between the word and the date is not: `re-read live 2026-09-18` carries no date the sweep can see,
and a note with none is reported as carrying none — stale by construction, since it cannot say when
it was true. Write the field on the **state** line and put the prose elsewhere.

**`base <sha>` is a field too**, and it is the second sign-off condition written down: the tip of
the head's **own** base ref — `split/3`, not `main` — that the head's checks ran against. A
`pull_request` job checks out the head merged with its base *as of that run*, so a head level with
its base has checks that attest to the tree USER would merge and a head one commit behind has
checks that attest to a merge nobody will ever perform. `sweep.py` reads the count live from
`compare`, and it reads this field to tell a head that owes a merge-down from a note that owes a
re-read. It is parsed the way `read <date>` is — through backticks and emphasis, so
``base **`4d96025`**`` is the same field — and the ref is named in the behind-count beside it
rather than between the field and its sha. A note carrying no `base` is silent, not stale: the
arithmetic is live and needs no note, and the field is there so that a reader of the note can do it
too.

**The log is the point.** It is what 🐦 Birdsong reads instead of re-deriving the queue from
GitHub, and the only trace an interactive session leaves of work that stayed on its own PR. One
line per turn, in the past tense, saying what *changed* — not what was scanned or read.

A merge of the target branch is the one to get right. It is support work, so it never earns its own
clause beside real work: a turn that merged `main` and then fixed three review threads logs the
three threads. But when it is the whole of the turn it is logged, plainly and alone — *"merged
`main`, nothing else"* — because the head did move and because a night that finished nothing should
read that way rather than vanish.
