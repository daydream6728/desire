#!/bin/bash
set -uo pipefail

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

log() { echo "session-start: $*" >&2; }

config="$(cd "$(dirname "$0")/../.." && pwd)/config.env"
agent="$(sed -n 's/^AGENT=//p' "$config" 2>/dev/null | tail -1)"
agent_email="$(sed -n 's/^AGENT_EMAIL=//p' "$config" 2>/dev/null | tail -1)"
if [ -n "$agent" ] && [ -n "$agent_email" ]; then
  git config --global --replace-all user.name "$agent"
  git config --global --replace-all user.email "$agent_email"
  log "git identity: $(git config --global user.name) <$(git config --global user.email)>"
else
  if [ ! -r "$config" ]; then
    log "config.env is unreadable"
  else
    [ -n "$agent" ] || log "config.env sets no AGENT"
    [ -n "$agent_email" ] || log "config.env sets no AGENT_EMAIL"
  fi
  cleared=yes
  for key in user.name user.email; do
    git config --global --unset-all "$key"
    case $? in 0 | 5) ;; *) cleared=no ;; esac
  done
  log "git identity NOT set (see above) — fix config.env before committing"
  [ "$cleared" = yes ] || log "could NOT clear the global identity: commits may" \
    "still be authored as $(git config --global user.name)" \
    "<$(git config --global user.email)> — clear it by hand"
fi

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
