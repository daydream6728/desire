# desire

> *Lilacs out of the dead land, mixing*
> 
> *Memory and desire, stirring*

Software engineering prompts inspired by the asymmetric board game Root:

- 🐦 [Birdsong](BIRDSONG.md) plans, asynchronously, before the day starts
- 🌤️ [Daylight](AGENTS.md#daylight) activates in every interactive session you open
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
   Use the [Amp setup](#amp) below, or have your harness explicitly read `AGENTS.md`. Configure scheduled
   runs separately with `Follow <path-to-desire>/BIRDSONG.md` (before your day) and
   `Follow <path-to-desire>/EVENING.md` (overnight), also loading the operating rules and memory.
   Moving the files to another harness does not migrate the schedules; check their timezone and
   access to every configured repo there.

Nothing in this repo names you: your login, your agent's, and the repos you work in are all in that
one `config.env`, in the repo that is yours. What is here is only the rules.

## Amp

Amp loads `AGENTS.md`. It does not
discover guidance in sibling repositories. Put a loader in Amp's global instructions so it also
applies when the working directory is a WORK_REPO. For orbs with the clones under
`~/workspace/repos/`, use this, adjusting the paths to your layout:

```text
Before the first response or task action, read ~/workspace/repos/desire/AGENTS.md.
For interactive sessions, follow its Daylight section. When explicitly requested, read
~/workspace/repos/desire/BIRDSONG.md or ~/workspace/repos/desire/EVENING.md instead
and do not execute Daylight. Read ~/workspace/repos/memory/AGENTS.md,
~/workspace/repos/memory/config.env and ~/workspace/repos/memory/README.md,
and the needed notes under ~/workspace/repos/memory/WORK/.
If any required file is unavailable, say so.
```

Daylight is part of the shared operating file, but only interactive sessions execute it.
Never place private config values in public guidance.

Skills in the sibling clones need discovery too. Add their `.agents/skills/` directories to
`amp.skills.path` and reload skills, or install them as personal/workspace skills. Confirm the
expected names appear in the session's skill list. A script such as the sweep can instead be run
by its explicit path; a linked skill can be read explicitly if it is not registered.

Use Amp's orb setup mechanism for dependency installation; `.claude/` startup hooks and permission
denies are Claude Code-specific. Follow [Identity and signing](OPERATIONS.md#identity-and-signing)
for authorship without replacing Amp's managed signer, and
[Watching a pull request](OPERATIONS.md#watching-a-pull-request) for event delivery.

## Verified commits

**Optional** — everything above works without this. What it buys: every commit the agents push
is signed so it shows the **Verified** badge. Authorship is required independently of signing.
Amp uses its managed signer; the setup below is only for Claude Code on the web, where the
environment's setup script signs and its variables set the identity, so every session of that
environment has both, the ones that never load the SessionStart hook included:

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
   silently does not run. The user-level settings file wires it by absolute path, so it pins
   where the `memory` clone lands, and skips it in a session that has no such clone. The hook
   ships with the seed and reads the `config.env` beside it, so both are in the one repo that
   names you. Its `autoMode` half is for [spawned sessions](#spawned-sessions):

```sh
#!/bin/bash
set -euo pipefail
mkdir -p /root/.claude
cat > /root/.claude/settings.json <<'EOF'
{"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command":
  "h=/home/user/memory/.claude/hooks/session-start.sh; [ ! -x $h ] || $h"}]}]},
 "autoMode": {"environment": [
  "$defaults",
  "Attaching any repo to the session with add_repo, read or push, is expected setup:",
  "the user's GitHub connection is a dedicated account that already limits which repos can be attached."
]}}
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

## Spawned sessions

**Optional**, for Claude Code on the web: what lets a session started by an agent attach your
other repos with nobody typing in it. A session's auto mode trusts the repo it started in and
nothing else, so a child spawned from this repo is refused when it attaches MEMORY_REPO or a work
repo, until you say so inside it. What it trusts is read from the user-level settings file,
`/root/.claude/settings.json` in the container, and from no file in a repo. The
[startup script above](#verified-commits) writes it: its `autoMode` lines are what a spawned
session needs, with or without the hook.

The repos a session can attach are whatever the GitHub account connected to Claude Code can
reach: check that account's access before pasting the line, which says it is a dedicated one. It
applies to sessions started after the change. The SessionStart hook merges its own
entries into the same file and keeps these.
