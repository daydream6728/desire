#!/bin/bash
# SessionStart hook — install the GitHub CLI (and jq) for the scheduled routines.
# Best-effort: it must NEVER block session start.
#
# Installs from Ubuntu's own apt repo (gh lives in noble universe) — the agent proxy
# allows archive.ubuntu.com but 403s github.com / cli.github.com release downloads.
set -uo pipefail   # deliberately no -e — an install failure must not abort the hook

# web / remote sessions only (the routines); do nothing on a local dev machine
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

log() { echo "session-start: $*" >&2; }

# AGENTS.md: "Commits carry that same identity, AGENT and AGENT_EMAIL, set on
# every clone before the first commit of a turn." Global, not per-repo, so it
# covers every WORK_REPO/MEMORY_REPO/DESIRE_REPO clone in the container
# without a hook in each. Only user.name/email — leaves the harness's own
# commit-signing config (signingkey, gpg.*) untouched.
#
# config.yaml (next to AGENTS.md) is the source of truth for AGENT/AGENT_EMAIL,
# read through sweep.py's own parser so the two readers cannot disagree and
# YAML quoting is honoured — not with sed, which would hand `"name" # note`
# to git verbatim, and not with yq, which shells out to the jq installed
# below, best-effort. There is no built-in identity to fall back on: a literal
# here would be a second place naming AGENT, which is what moving the config
# into one file removed, and it would stamp the old name on every commit of a
# session whose config.yaml was mid-rotation. So a file that cannot be read,
# does not parse, or sets neither key leaves the identity alone and says which
# of the three it was; committing then fails loudly instead of quietly
# attributing the work to the wrong agent.
config_root="$(cd "$(dirname "$0")/../.." && pwd)"
if identity="$(python3 - "$config_root" <<'PY'
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / ".agents/skills/sweep"))
import sweep

try:
    setup = sweep.config(root / "config.yaml")
except OSError as error:
    sys.exit(f"session-start: config.yaml is unreadable: {error}")
except Exception as error:  # a line outside the subset config() parses
    sys.exit(f"session-start: config.yaml does not parse: {error!r}")
missing = [key for key in ("AGENT", "AGENT_EMAIL")
           if not str(setup.get(key, "")).strip()]
if missing:
    sys.exit(f"session-start: config.yaml sets no {' and no '.join(missing)}")
print(setup["AGENT"])
print(setup["AGENT_EMAIL"])
PY
)"; then
  git config --global --replace-all user.name \
    "$(printf '%s\n' "$identity" | sed -n 1p)"
  git config --global --replace-all user.email \
    "$(printf '%s\n' "$identity" | sed -n 2p)"
  log "git identity: $(git config --global user.name) <$(git config --global user.email)>"
else
  # Clearing rather than leaving what was there: a stale global identity from
  # the image or an earlier session would commit under itself, quietly, while
  # this line claims nothing is set. Unset, `git commit` stops and asks.
  # Exit 5 is "nothing to unset", which is already the wanted state; anything
  # else means the line below would be a lie, so it is said out loud instead
  # of swallowed. git's own error goes to stderr with it.
  cleared=yes
  for key in user.name user.email; do
    git config --global --unset-all "$key"
    case $? in 0 | 5) ;; *) cleared=no ;; esac
  done
  log "git identity NOT set (see above) — fix config.yaml before committing"
  [ "$cleared" = yes ] || log "could NOT clear the global identity: commits may" \
    "still be authored as $(git config --global user.name)" \
    "<$(git config --global user.email)> — clear it by hand"
fi

pkgs=()
command -v jq >/dev/null 2>&1 || pkgs+=(jq)
command -v gh >/dev/null 2>&1 || pkgs+=(gh)

if [ ${#pkgs[@]} -gt 0 ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq >/dev/null 2>&1 || true
  if apt-get install -y -qq "${pkgs[@]}" >/dev/null 2>&1; then
    log "installed: ${pkgs[*]}"
  else
    log "apt install failed for: ${pkgs[*]} — the GitHub MCP tools remain available"
  fi
fi

# gh reads GH_TOKEN / GITHUB_TOKEN automatically (both are set in this environment)
[ -n "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ] || log "note: no GH_TOKEN/GITHUB_TOKEN in env — gh will be unauthenticated"

command -v gh >/dev/null 2>&1 && log "$(gh --version | head -1)" || true
exit 0
