# TODO

> i have been preparing a github project to track the agent's tasks: https://github.com/users/daydream6728/projects/2
> added nightmare6728 as a collaborator.
>
> what if instead of storing the memory in the contents of daydream6728/memory, we instead store it as issues on the memory repo and track them inside the github project. i added a special "Claude conversation" custom field on issues which would let me click on a link and directly hop into the right claude code conversation.
> the memory in TURNS and README.md would still exist but only be loose reflections of what happened on the github project.
>
> i want you to rethink this agentic setup by ensuring that everything the agent does must be reflected on the github project and issue contents in the memory repo.

USER's answers, this session:
- the board is written by an Action holding a PAT, never by the agents directly
- every unit of work gets an issue, work-repo PRs mirrored
- *"the daily memory PR is just another task in the project, except that its a PR and
  not an issue. otherwise works exactly the same"*

- [x] `AGENTS.md`: Memory becomes the board — one item per unit of work, the
      agent-writable surface, the status labels, the conversation log
- [x] `BIRDSONG.md` / `DAYLIGHT.md` / `EVENING.md`: each phase said in items
- [x] `config.env`: `PROJECT`, so nothing hard-codes the board's URL
- [x] `README.md`: Get started gains the project, the field, the PAT and the Action
- [x] `CHANGELOG.md`: what this replaces
- [ ] MEMORY_REPO: the sync Action, its `AGENTS.md` and an issue template — its own PR
- [x] the ruling as an open issue on DESIRE_REPO, closed by this PR
