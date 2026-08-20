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
# config.yaml (next to AGENTS.md) is the source of truth for AGENT/AGENT_EMAIL.
# Read with sed, not yq: yq here shells out to jq, and jq is only installed
# below, best-effort. The literal fallback only fires if config.yaml can't
# be read at all.
config_root="$(cd "$(dirname "$0")/../.." && pwd)"
scalar() { sed -n "s/^$1:[[:space:]]*//p" "$config_root/config.yaml" 2>/dev/null | head -1; }
agent="$(scalar AGENT)"; agent="${agent:-toumix-agents}"
agent_email="$(scalar AGENT_EMAIL)"; agent_email="${agent_email:-agents@toumi.email}"
git config --global --replace-all user.name "$agent"
git config --global --replace-all user.email "$agent_email"
log "git identity: $(git config --global user.name) <$(git config --global user.email)>"

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
