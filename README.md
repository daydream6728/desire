# desire

> *Lilacs out of the dead land, mixing*
> 
> *Memory and desire, stirring*

Software engineering prompts inspired by the asymmetric board game Root:

- 🐦 [Birdsong](BIRDSONG.md) plans, asynchronously, before the day starts
- 🌤️ [Daylight](DAYLIGHT.md) activates in every interactive session you open
- 🌙 [Evening](EVENING.md) reviews and implements, overnight, what you approved

[AGENTS.md](AGENTS.md) is the operating base they all follow: the two layers of memory, what
authorizes a change — with the values it runs on in [config.env](config.env). It is deliberately
short (under a hundred lines with the phase files) because every line of it is loaded into every
session. Some guiding principles:

- **Asynchronous feedback via GitHub PRs**, you don't need an interactive chat to get stuff done.
- **Synchronous feedback via chat sessions**, but they start with the bigger picture in mind.
- **Agents open issues when the rules clash**, at your request they open a PR with updated rules.

## Get started

1) Open a new GitHub account for your agents, add it as collaborator to your fork for this repo,
   and name it `AGENT` in [`config.env`](config.env) — with `USER` and `AGENT_EMAIL` beside it.
2) Enable the issues tab on your fork, under Settings → Features. A fork ships with it **off**,
   and the agents park every ruling there — an empty tab reads as *nothing ruled*, not as *no tab*.
3) Create a new GitHub repo (e.g. called `memory`), set it as `MEMORY_REPO` in that same file,
   set your fork as `DESIRE_REPO`, and list the repos your agents work in under `WORK_REPOS`.
4) Create a GitHub **project**, add `AGENT` to it as a collaborator, give it a text field named
   exactly `Claude conversation`, and put its URL in `PROJECT`. It is where the work lives — see
   [The project](#the-project) for the token it needs to stay in step.
5) Integrate it to your model provider, adding the `memory` and `desire` repos alongside your work.

**Pro tip:** Ask your 🌤️ Daylight session for its password to check it actually loaded the prompt.

## The project

Every unit of work the agents do is an item there: an issue of `MEMORY_REPO`, or the day's memory
pull request. The files under `MEMORY_REPO` — the turn journal and a standing README — are
reflections of it, not the state itself.

The agents cannot write a project field. Projects are GraphQL-only and agent sessions are served
REST, so the board is kept in step by an Action in `MEMORY_REPO` holding a token of yours, and the
agents write only what an issue can carry — a `status:` label, a `## Conversations` line, a
comment. Wiring it up:

1) `.github/workflows/project-sync.yml` in `MEMORY_REPO` — it fires on every issue, comment and
   pull request event and writes two fields: `Status`, from the item's one `status:` label, and
   `Claude conversation`, from the last line of the body's `## Conversations` block. Hourly and
   on `workflow_dispatch` it reconciles every open item instead, which is the repair for a
   missed event and the pass an agent can trigger itself. `Status` is written only by the events
   that moved it, never by an edit or a reconcile: a card you drag stays where you dragged it,
   and the label is what an agent changes to move one.
2) A fine-grained personal access token with **read and write** on your projects and read on the
   repo, stored as the `PROJECT_TOKEN` secret of `MEMORY_REPO`. It is yours, not `AGENT`'s: the
   project is a user project and only its owner can grant it.
3) Status options on the project matching the labels — `Queued`, `In progress`, `Blocked`,
   `In review`, `Done`. A label with no matching option is skipped rather than failing the run,
   so renaming one loses the sync for that state and nothing else.

## Verified commits

**Optional** — everything above works without this. What it buys: every commit the agents push
is authored by `AGENT` rather than a default identity, and signed so it shows the **Verified**
badge — one glance tells a real agent commit from anything else. The SessionStart hook does
both; wiring it up, on Claude Code on the web:

1) Generate a passphrase-free SSH key: `ssh-keygen -t ed25519 -f ~/.ssh/agents_signing -N ''` —
   under `~/.ssh`, never in a checkout, where a broad `git add` could commit it.
2) Register `~/.ssh/agents_signing.pub` on `AGENT`'s account as a **signing key** — not an
   authentication key: leaked, it can only forge the badge, revoked by deleting the public half.
3) Paste the private key into `AGENTS_SIGNING_KEY` in the environment's variables; a session
   without it commits unsigned rather than failing.
4) Paste this into the environment's startup script. A multi-repo session opens in the parent
   directory of its clones, so no repo is the project directory, `desire/.claude/settings.json`
   never loads, and the hook silently does not run — no identity, no signing. A workspace-level
   settings file wires it by absolute path, so it pins where the `desire` clone lands:

```sh
mkdir -p /home/user/.claude
cat > /home/user/.claude/settings.json <<'EOF'
{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"/home/user/desire/.claude/hooks/session-start.sh"}]}]}}
EOF
```
