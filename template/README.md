# template

The seed of a MEMORY_REPO. Nothing here is loaded by a session: it is copied once, into a fresh
private repository, and then it is that repository's to rewrite — with one exception,
`.agents/skills/sweep/`, which is the same file running in both places. **A change to the sweep
lands in this copy and in the live one the same turn**: this is the public half, so it is the one
anyone can read, and the two drifting apart is a sweep nobody can review.

The two clones sit side by side, and these run from the directory holding them — the same layout
a session opens in:

```sh
cd "$(dirname "$(pwd)")"          # from inside desire; skip if you are already beside it
gh repo create <you>/memory --private
git clone https://github.com/<you>/memory && cp -r desire/template/memory/. memory/
"${EDITOR:-vi}" memory/config.env   # every value is a placeholder
cd memory && git add -A && git commit -m "Seed the memory" && git push
```

Then fill `config.env` — it is the one file that names you, your agent account and the repos they
work in, and it is why nothing else in `desire` needs to. It is commented, and the readers skip
`#` lines, so the notes stay in the file you edit.

The sweep reads `config.env` three directories up from itself, which is your memory clone's root
once it is seeded — the same in this template, so `pytest .agents/skills/sweep/` passes here as it
will there. Nothing is searched for and no repository name is hard-coded anywhere.

What you get is empty on purpose. `README.md` is a board with no state on it yet, `USER_TODO.md`
a list with nothing on it, and the three `TEMPLATE.md` files are shapes rather than content — the
first turn writes the real thing. Leave the templates in place: they are what an agent reads when
it writes its first `WORK/` file, and deleting them costs you the shape.

`memory/.github/PULL_REQUEST_TEMPLATE.md` is the day PR's shape, the one 🐦 Birdsong writes.
