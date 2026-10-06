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
MEMORY_REPO. It is kept to the rules themselves because every line of it is loaded into every
session; the machinery behind them, needed only when something misbehaves, lives in
[OPERATIONS.md](OPERATIONS.md), which is not. Some guiding principles:

- **Asynchronous feedback via GitHub PRs**, you don't need an interactive chat to get stuff done.
- **Synchronous feedback via chat sessions**, but they start with the bigger picture in mind.
- **Agents open issues when the rules clash**, at your request they open a PR with updated rules.

## Get started

1) Open a new GitHub account for your agents, add it as collaborator to your fork for this repo.
2) Enable the issues tab on your fork, under Settings → Features. A fork ships with it **off**,
   and the agents park every ruling there — an empty tab reads as *nothing ruled*, not as *no tab*.
3) Create a new **private** GitHub repo (e.g. called `memory`) and seed it from
   [`template/`](template/): the board, the standing note each open item gets, the day PR's shape,
   the sweep, and a `config.env` in which every value is a placeholder. Fill that file in — `AGENT`
   and `AGENT_EMAIL` for the new account, `USER` for yours, `MEMORY_REPO` for this new repo,
   `DESIRE_REPO` for your fork, and the repos your agents work in under `WORK_REPOS`. It lives
   there and not here because this repo is public and the repos you work in need not be, and the
   sweep is seeded beside it because that is the file it reads.
4) Integrate it to your model provider, adding the `memory` and `desire` repos alongside your work.

Nothing in this repo names you: your login, your agent's, and the repos you work in are all in that
one `config.env`, in the repo that is yours. What is here is only the rules.

**Pro tip:** Ask your 🌤️ Daylight session for its password to check it actually loaded the prompt.

## Keep Codex pull requests listening

Each Codex task that opens a pull request schedules its own heartbeat. It checks for your feedback
and valid in-scope bug or style reports from anyone, acts on them, backs off while the pull request
is idle, and deletes itself when the pull request merges or closes. No setup.

## Verified commits

**Optional** — everything above works without this. What it buys: every commit the agents push
is authored by `AGENT` rather than a default identity, and signed so it shows the **Verified**
badge — one glance tells a real agent commit from anything else. The environment's setup script
signs and its variables set the identity, so every session of that environment has both, the
ones that never load the SessionStart hook included; wiring it up, on Claude Code on the web:

1) Generate a passphrase-free GPG signing key for `AGENT` and its one-line export, outside any
   checkout, where a broad `git add` could commit it:
   ```sh
   gpg --batch --passphrase '' --quick-gen-key "<AGENT> <<AGENT_EMAIL>>" ed25519 sign 1y
   gpg --export-secret-keys --armor <AGENT_EMAIL> | base64 -w0 > agents_signing_key.b64
   ```
2) Register `gpg --armor --export <AGENT_EMAIL>` on `AGENT`'s account as a **GPG key**. Leaked,
   it can only forge the badge, revoked by deleting it there.
3) Set the identity in the environment's variables, one per line, no quotes — a variables
   line keeps them as part of the value:
   ```
   GIT_CONFIG_COUNT=2
   GIT_CONFIG_KEY_0=user.name
   GIT_CONFIG_VALUE_0=<AGENT>
   GIT_CONFIG_KEY_1=user.email
   GIT_CONFIG_VALUE_1=<AGENT_EMAIL>
   ```
   Only these two keys: git reads `GIT_CONFIG_*` after every config file, which is why they
   outlive the default identity the environment writes to `~/.gitconfig` after the setup
   script, and why a signing key left among them would override the one below.
4) Paste this into the environment's setup script, with the contents of `agents_signing_key.b64`
   between the quotes, then delete that file. The key goes in the script itself: the setup
   script does not see the environment's variables, which only reach the session after it. The
   image ships `gpg` but not `ssh-keygen`, so nothing is installed. The first lines wire the
   SessionStart hook: a multi-repo session opens in the parent directory of its clones, so no
   repo is the project directory, `memory/.claude/settings.json` never loads, and the hook
   silently does not run. A workspace-level settings file wires it by absolute path, so it pins
   where the `memory` clone lands. The hook ships with the seed and reads the `config.env`
   beside it, so both are in the one repo that names you:

```sh
#!/bin/bash
set -euo pipefail
mkdir -p /home/user/.claude
cat > /home/user/.claude/settings.json <<'EOF'
{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"/home/user/memory/.claude/hooks/session-start.sh"}]}]}}
EOF

KEY_B64='<one line of agents_signing_key.b64>'
printf '%s' "$KEY_B64" | base64 -d | gpg --batch --import
FPR=$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr/{print $10; exit}')
echo "$FPR:6:" | gpg --batch --import-ownertrust
git config --global gpg.format openpgp
git config --global user.signingkey "$FPR"
git config --global commit.gpgsign true
echo "signing key imported: $FPR"
```

The check that it worked, in a new session: `git config user.name` prints `AGENT`, and after
`git commit --allow-empty -m test`, `git log -1 --show-signature` prints `Good signature from
"<AGENT> <<AGENT_EMAIL>>"` with `AGENT` as author and committer.

The hook can still sign without the setup script, from an SSH key in `AGENTS_SIGNING_KEY`
generated with `ssh-keygen -t ed25519 -N ''` and registered as a **signing key**; it does so
only in the sessions that load it, so the setup script is the one that covers every session.
