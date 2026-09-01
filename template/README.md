# template

The seed of a MEMORY_REPO. Nothing here is loaded by a session: it is copied once, into a fresh
private repository, and then it is that repository's to rewrite.

```sh
gh repo create <you>/memory --private
git clone https://github.com/<you>/memory && cp -r desire/template/memory/. memory/
$EDITOR memory/config.env   # every value is a placeholder
cd memory && git add -A && git commit -m "Seed the memory" && git push
```

Then fill `config.env` — it is the one file that names you, your agent account and the repos they
work in, and it is why nothing else in `desire` does. The prompts read it from the root of the
MEMORY_REPO clone, so a session needs both clones side by side.

What you get is empty on purpose. `README.md` is a board with no state on it yet, `USER_TODO.md`
a list with nothing on it, and the three `TEMPLATE.md` files are shapes rather than content — the
first turn writes the real thing. Leave the templates in place: they are what an agent reads when
it writes its first `PRS/` file, and deleting them costs you the shape.

`memory/.github/PULL_REQUEST_TEMPLATE.md` is the day PR's shape, the one 🐦 Birdsong writes.
