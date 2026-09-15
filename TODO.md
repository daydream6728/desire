> Read desire/BIRDSONG.md and run a 🐦 Birdsong turn for today.

Tooling half of the turn: `sweep.py` and its public copy under `template/`.
Stacked on [#27](https://github.com/daydream6728/desire/pull/27), which is
still unmerged and already rewrites both sweep files.

- [ ] `sweep.py` checks `AGENTS.md`'s third sign-off condition — no review
      thread waiting on an agent — which no tool of ours has ever checked
- [ ] The resolution state comes from `pulls/<n>/ccr/review_threads`, the REST
      stand-in the GraphQL 403 names in its own body
- [ ] A runtime that serves no such route reports the condition unchecked
      rather than clean
- [ ] Tests for each case, and the two copies byte-identical again
- [ ] `OPERATIONS.md` says what the check flags; `CHANGELOG.md` entry
