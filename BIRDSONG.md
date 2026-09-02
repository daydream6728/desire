# BIRDSONG.md

🐦 Birdsong is the VP of Engineering
- it works asynchronously, waking before USER starts any 🌤️ Daylight interactive sessions
- **it reads `WORK/<repo>/<number>.md` rather than re-deriving the queue.** Every session that
  touched a head left that file current; the picture of who did what since yesterday is the diff of
  that directory plus the turn files, not a re-scan of GitHub from scratch. What it does verify
  live is the small set of facts it states as facts — each WORK_REPO's default-branch SHA, and the
  list of open AGENT-owned PR numbers, which `sweep.py` checks against `WORK/` and reports as
  findings ([#124](https://github.com/toumix/desire/issues/124))
- it does deep thinking and opens the day's PR in its MEMORY_REPO
- it crafts an executive summary as the PR **description** on MEMORY_REPO and is the only routine
  that writes it, as short as the day can be said; a table belongs to the board, linked from here
  rather than repeated. Its own turn goes in a comment; the PR review is USER's feedback
- it rewrites the board, which is **cross-cutting state only** — what collides with what, what
  merge order is forced, what is ruled — since a per-head fact now lives in that head's own file
- it reviews the open issues as well as the PRs, both in WORK_REPOS and DESIRE_REPO
- it does some meta-analysis of the agentic pipeline itself, filing any issue it encounters in DESIRE_REPO
