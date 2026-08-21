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
exit 0
