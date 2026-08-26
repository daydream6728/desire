# TODO

USER, [#113](https://github.com/toumix/desire/pull/113), 2026-08-26, verbatim:

> 2

Answering the second ask of the description: **suppress what the pipeline has already
seen** — report an unanswered USER comment when it is inside the window **or** carries
no 👀, so triaging the tail once quiets it and anything new is loud from the moment it
lands.

## Work

- [x] `sweep.py`: one place deciding whether USER is still asking, used by both branches
- [x] `sweep.py`: the usage line says what `--since` windows now
- [x] `AGENTS.md`: a 👀 quiets an old question, which is what makes the sweep readable
- [x] `CHANGELOG.md`: fold into the entry, it has not landed yet
- [ ] measure the discopy sweep again and put the new number on the PR
