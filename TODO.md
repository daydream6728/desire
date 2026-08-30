# TODO.md

Prompt, from [memory#9](https://github.com/daydream6728/memory/issues/9), verbatim:

> Follow-up named in [desire#5](https://github.com/daydream6728/desire/issues/5), now that the project is the memory: nothing yet checks that the board has no gaps.
>
> The three checks decided earlier, all readable over REST without touching the project (GraphQL is refused to agent sessions):
>
> - an AGENT-owned head in WORK_REPOS with no mirroring item in MEMORY_REPO
> - an open item carrying no `status:` label, or more than one
> - a stale mirror is an item whose head merged or closed and which is still open

- [WIP] @fl5143-2026-08-30 01:45 implement the three checks in `sweep.py`, run on the MEMORY_REPO sweep
