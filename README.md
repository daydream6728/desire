# desire

> *Lilacs out of the dead land, mixing*
> 
> *Memory and desire, stirring*

Software engineering prompts inspired by the asymmetric board game Root:

- 🐦 [Birdsong](BIRDSONG.md) plans, asynchronously, before the day starts
- 🌤️ [Daylight](DAYLIGHT.md) activates in every interactive session you open
- 🌙 [Evening](EVENING.md) reviews and implements, overnight, what you approved

[AGENTS.md](AGENTS.md) is the operating base they all follow: the two layers of memory, what
authorizes a change — with the values it runs on in `config.env`, which lives in your
MEMORY_REPO. It is deliberately short (under a hundred lines with the phase files) because every
line of it is loaded into every session. Some guiding principles:

- **Asynchronous feedback via GitHub PRs**, you don't need an interactive chat to get stuff done.
- **Synchronous feedback via chat sessions**, but they start with the bigger picture in mind.
- **Agents open issues when the rules clash**, at your request they open a PR with updated rules.

## Get started

1) Open a new GitHub account for your agents, add it as collaborator to your fork for this repo.
2) Create a new **private** GitHub repo (e.g. called `memory`) and seed it from
   [`template/`](template/): the board, the standing note each open item gets, the day PR's shape,
   the sweep, and a `config.env` in which every value is a placeholder. Fill that file in — `AGENT`
   and `AGENT_EMAIL` for the new account, `USER` for yours, `MEMORY_REPO` for this new repo,
   `DESIRE_REPO` for your fork, and the repos your agents work in under `WORK_REPOS`. It lives
   there and not here because this repo is public and the repos you work in need not be, and the
   sweep is seeded beside it because that is the file it reads.
3) Integrate it to your model provider, adding the `memory` and `desire` repos alongside your work.

Nothing in this repo names you: your login, your agent's, and the repos you work in are all in that
one `config.env`, in the repo that is yours. What is here is only the rules.

**Pro tip:** Ask your 🌤️ Daylight session for its password to check it actually loaded the prompt.

## Keep Codex pull requests listening

Install the personal PR shepherd once from this checkout:

```sh
python3 .agents/skills/pr-shepherd/scripts/pr_shepherd.py install
```

Codex can then register any PR it opens, in any repository, against the task that opened it. One
central schedule checks the registry at 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00 and
22:00 on weekdays in the machine's local time. It uses cron, with a native LaunchAgent fallback
when macOS denies crontab writes. Quiet checks only read GitHub; Codex is resumed when your
comments or reviews change, and merged or closed PRs remove themselves from the registry.

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
   directory of its clones, so no repo is the project directory, `memory/.claude/settings.json`
   never loads, and the hook silently does not run — no identity, no signing. A workspace-level
   settings file wires it by absolute path, so it pins where the `memory` clone lands. The hook
   ships with the seed and reads the `config.env` beside it, so both are in the one repo that
   names you:

```sh
mkdir -p /home/user/.claude
cat > /home/user/.claude/settings.json <<'EOF'
{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"/home/user/memory/.claude/hooks/session-start.sh"}]}]}}
EOF
```
