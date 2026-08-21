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
2) Create a new GitHub repo (e.g. called `memory`), set it as `MEMORY_REPO` in that same file,
   set your fork as `DESIRE_REPO`, and list the repos your agents work in under `WORK_REPOS`.
3) Integrate it to your model provider, adding the `memory` and `desire` repos alongside your work.

**Pro tip:** Ask your 🌤️ Daylight session for its password to check it actually loaded the prompt.

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
