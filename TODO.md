> Read desire/EVENING.md and run a 🌙 Evening turn for tonight.

Tonight's head: the instrument half of
[#49](https://github.com/daydream6728/desire/issues/49) — `sweep.py` reads
`pulls/<n>/comments`, `pulls/<n>/ccr/review_threads` and `pulls/<n>`, never
`pulls/<n>/reviews`, so a pull request **review** of USER's reaches the pipeline
through no instrument it owns. Stacked on [#48](https://github.com/daydream6728/desire/pull/48),
which touches the same two files.

- [ ] Reproduce the blindness: a fixture where USER's `APPROVED` review is the
      only thing on a pull request, and the sweep reports nothing
- [ ] Read `pulls/<n>/reviews` and report USER's unanswered reviews, with the
      state, in both copies of `sweep.py` the same turn
- [ ] A test for each case: the approval nobody answered, the one an agent
      answered after, a review of somebody else's, one of ours from USER's
      handle, and an issue (which has no reviews)
- [ ] `cmp` both files against MEMORY_REPO's live ones, and run the suite
      against the file this replaces to show the tests are about the bug
- [ ] The `AGENTS.md` TRUSTED-list wording stays out: that half is a rule
      change and waits on #49's 🚀
