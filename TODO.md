# TODO

> Read desire/EVENING.md and run a 🌙 Evening turn for tonight.

Tonight's head is the tooling half of
[#30](https://github.com/daydream6728/desire/issues/30) — nothing in the pipeline enumerates *every
repo in play*, so `config.env` can name four `WORK_REPOS` while twenty-two consecutive turns sweep
three of them and read the word `clean`. `AGENTS.md` asks for the sweep *"over every open PR and
issue of every repo in play"* and `sweep.py` takes one repo per invocation, never reading the list:
`WORK_REPOS` is used twice, both times as a membership test on the repo the agent already typed. The
issue's own second cause — `rel-int/discopy` and `rel-int/lambeq` being outside this session's
GitHub scope — is USER's half and is not touched here. Every point below is the issue's first
proposal.

- [ ] `everywhere(setup)`: the repos in play as a list, MEMORY_REPO then DESIRE_REPO then
      `WORK_REPOS`, de-duplicated and order-preserving, so two turns read the same list in the same
      order
- [ ] `sweep.py` with no repo argument sweeps every one of them in turn, and an unreadable repo is
      one finding among the others rather than the whole run's exit code, so one denied repo cannot
      hide what the readable ones found
- [ ] `clean` becomes a claim about the configuration: printed only when the invocation covered
      every repo in play, read all of them and found nothing. A narrower invocation says what it
      covered and names what it left out
- [ ] Exit codes stay the contract the docstring states: 2 when a repo in play could not be read, 1
      on findings, 0 otherwise — a one-repo invocation with no finding stays 0, since sweeping the
      slow repo alone is how a turn is meant to work
- [ ] Tests for the new pure functions and for the multi-repo loop's exit code
- [ ] `OPERATIONS.md`'s "Reading the sweep" and the module docstring say the new usage
- [ ] `CHANGELOG.md` entry
- [ ] Both copies the same turn: `template/memory/.agents/skills/sweep/` here, the live
      `.agents/skills/sweep/` in MEMORY_REPO's day PR
