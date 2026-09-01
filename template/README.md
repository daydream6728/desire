# template

The seed of a MEMORY_REPO. Nothing here is loaded by a session: it is copied once, into a fresh
private repository, and then it is that repository's to rewrite.

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

**One thing to know about timing**: the seed puts `config.env` at the root of your memory clone,
which is where [desire#131](https://github.com/toumix/desire/pull/131) moves it. Until that merges,
the live values are still read from `desire/config.env`, so fill that one and keep the seed as the
copy that takes over.

What you get is empty on purpose. `README.md` is a board with no state on it yet, `USER_TODO.md`
a list with nothing on it, and the three `TEMPLATE.md` files are shapes rather than content — the
first turn writes the real thing. Leave the templates in place: they are what an agent reads when
it writes its first `WORK/` file, and deleting them costs you the shape.

`memory/.github/PULL_REQUEST_TEMPLATE.md` is the day PR's shape, the one 🐦 Birdsong writes.
