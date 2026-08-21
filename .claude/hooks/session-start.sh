#!/bin/bash
set -uo pipefail

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

log() { echo "session-start: $*" >&2; }

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
except Exception as error:
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

[ -n "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ] || log "note: no GH_TOKEN/GITHUB_TOKEN in env — gh will be unauthenticated"

command -v gh >/dev/null 2>&1 && log "$(gh --version | head -1)" || true
exit 0
