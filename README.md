# desire

> *Lilacs out of the dead land, mixing*
> 
> *Memory and desire, stirring*

Software engineering prompts inspired by the asymmetric board game Root:

- 🐦 [Birdsong](BIRDSONG.md) plans, asynchronously, before the day starts
- 🌤️ [Daylight](DAYLIGHT.md) activates in every interactive session you open
- 🌙 [Evening](EVENING.md) reviews and implements, overnight, what you approved

[AGENTS.md](AGENTS.md) is the operating base they all follow: the two layers of memory, what
authorizes a change — with the values it runs on in [config.yaml](config.yaml). It is deliberately
short (under a hundred lines with the phase files) because every line of it is loaded into every
session. Some guiding principles:

- **Asynchronous feedback via GitHub PRs**, you don't need an interactive chat to get stuff done.
- **Synchronous feedback via chat sessions**, but they start with the bigger picture in mind.
- **Agents open issues when the rules clash**, at your request they open a PR with updated rules.

## Get started

1) Open a new GitHub account for your agents, add it as collaborator to your fork for this repo,
   and name it `AGENT` in [`config.yaml`](config.yaml) — with `USER` and `AGENT_EMAIL` beside it.
2) Create a new GitHub repo (e.g. called `memory`), set it as `MEMORY_REPO` in that same file,
   set your fork as `DESIRE_REPO`, and list the repos your agents work in under `WORK_REPOS`.
3) Integrate it to your model provider, adding the `memory` and `desire` repos alongside your work.

**Pro tip:** Ask your 🌤️ Daylight session for its password to check it actually loaded the prompt.
