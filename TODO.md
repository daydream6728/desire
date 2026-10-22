# TODO

> Read desire/EVENING.md and run a 🌙 Evening turn for tonight.

The head: `verdicts(...)`, the review reader [#50](https://github.com/daydream6728/desire/pull/50)
added, reports a review of USER's as answered when **anybody but USER** posted after it. Measured
tonight on `discopy#813`: USER's `APPROVED` of `2026-10-21T09:09:59Z` is hidden by
toumix-agents' own comment of `16:06:15Z`, so the sweep printed nothing about the one signal
desire#49 built it to see.

- [ ] `ours(post, setup)`: a post the pipeline wrote — AGENT's handle, or USER's with an
      AGENT_FOOTER — and `verdicts` silences a review on that, not on `answered`
- [ ] `authored(repo, number, body, setup)`: a pull request of ours in any repo, with `owned`
      delegating to it for the WORK_REPOS half
- [ ] an unanswered review on a head that is **not** ours is printed as context, not counted as a
      finding: `AGENTS.md` keeps us off it and a review carries no reactions endpoint, so no move
      of ours could ever clear one
- [ ] tests for all three, and the same file in `template/memory/` and in MEMORY_REPO's clone
