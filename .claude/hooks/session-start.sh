#!/bin/bash
# SessionStart hook — install the GitHub CLI (and jq) for the scheduled routines,
# and turn on commit signing when the environment carries the signing key.
# Best-effort: it must NEVER block session start.
#
# Installs from Ubuntu's own apt repo (gh lives in noble universe) — the agent proxy
# allows archive.ubuntu.com but 403s github.com / cli.github.com release downloads.
set -uo pipefail   # deliberately no -e — an install failure must not abort the hook

# web / remote sessions only (the routines); do nothing on a local dev machine
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

log() { echo "session-start: $*" >&2; }

pkgs=()
command -v jq >/dev/null 2>&1 || pkgs+=(jq)
command -v gh >/dev/null 2>&1 || pkgs+=(gh)
# git signs via `ssh-keygen -Y sign`, absent from the base image
[ -n "${AGENTS_SIGNING_KEY:-}" ] && ! command -v ssh-keygen >/dev/null 2>&1 && pkgs+=(openssh-client)

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

# --- commit signing ---------------------------------------------------------
# AGENTS_SIGNING_KEY is an SSH private key whose public half is registered on
# AGENT's account as a signing key only — it cannot authenticate or push.
# Environment variables are readable by every session in the environment, so
# nothing more capable than a signing key ever goes in one.
# Start from unsigned every run — only the success branch turns signing on, so
# stale config cannot outlive its key if $HOME ever persists between sessions.
git config --global --unset-all commit.gpgsign 2>/dev/null || true
if [ -n "${AGENTS_SIGNING_KEY:-}" ] && ! command -v ssh-keygen >/dev/null 2>&1; then
  log "AGENTS_SIGNING_KEY set but ssh-keygen unavailable — commits stay unsigned"
elif [ -n "${AGENTS_SIGNING_KEY:-}" ]; then
  key="$HOME/.ssh/agents_signing"
  mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
  printf '%s\n' "$AGENTS_SIGNING_KEY" > "$key"   # ssh rejects a key missing its final newline
  chmod 600 "$key"
  if ssh-keygen -y -P '' -f "$key" > "$key.pub" 2>/dev/null; then
    git config --global gpg.format ssh
    git config --global user.signingkey "$key"
    git config --global commit.gpgsign true
    log "commit signing on ($(ssh-keygen -lf "$key.pub" | awk '{print $2}'))"
  else
    rm -f "$key" "$key.pub"
    log "AGENTS_SIGNING_KEY is not a valid passphrase-free SSH key — commits stay unsigned"
  fi
else
  log "no AGENTS_SIGNING_KEY in env — commits stay unsigned"
fi

exit 0
