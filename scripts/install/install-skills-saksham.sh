#!/usr/bin/env bash
# Install only the saksham-supported skill subset from this checkout.
# Hobby/fab/robotics skills stay in the tree but are not linked by default.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"

# Supported for day-to-day saksham CAD / drawing / review work.
saksham_SKILLS=(
  cad
  cad-viewer
  dxf
  step-parts
)

# Reuse the full installer by temporarily restricting list-skills via env.
# Prefer an explicit loop so we never depend on list-skills filtering.
ALL_AGENTS=(
  codex
  claude
  gemini
  universal
  project
)

SELECTED_AGENTS=()
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  scripts/install/install-skills-saksham.sh [--agent <agent>]... [--all] [--dry-run]

Links only: cad, cad-viewer, dxf, step-parts.
Same agent destinations as scripts/install/install-skills.sh.
EOF
}

canonical_agent() {
  case "$1" in
    codex) printf 'codex\n' ;;
    claude|claude-code) printf 'claude\n' ;;
    gemini|gemini-cli) printf 'gemini\n' ;;
    universal|agents) printf 'universal\n' ;;
    project|repo) printf 'project\n' ;;
    *)
      echo "Unknown agent: $1" >&2
      return 1
      ;;
  esac
}

agent_destination() {
  case "$1" in
    codex) printf '%s\n' "${CODEX_HOME:-$HOME/.codex}/skills" ;;
    claude) printf '%s\n' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills" ;;
    gemini) printf '%s\n' "$HOME/.gemini/skills" ;;
    universal) printf '%s\n' "${XDG_CONFIG_HOME:-$HOME/.config}/agents/skills" ;;
    project) printf '%s\n' "$REPO_ROOT/.agents/skills" ;;
    *) return 1 ;;
  esac
}

contains_agent() {
  local needle="$1" agent
  for agent in "${SELECTED_AGENTS[@]+"${SELECTED_AGENTS[@]}"}"; do
    if [ "$agent" = "$needle" ]; then
      return 0
    fi
  done
  return 1
}

add_agent() {
  local agent
  agent="$(canonical_agent "$1")"
  if ! contains_agent "$agent"; then
    SELECTED_AGENTS+=("$agent")
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -a|--agent)
      shift
      add_agent "${1:?--agent requires a name}"
      shift
      ;;
    --all)
      SELECTED_AGENTS=("${ALL_AGENTS[@]}")
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "${#SELECTED_AGENTS[@]}" -eq 0 ]; then
  add_agent project
fi

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf 'dry-run:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

for agent in "${SELECTED_AGENTS[@]}"; do
  dest="$(agent_destination "$agent")"
  run mkdir -p "$dest"
  for skill in "${saksham_SKILLS[@]}"; do
    src="$REPO_ROOT/skills/$skill"
    if [ ! -d "$src" ]; then
      echo "Missing skill directory: $src" >&2
      exit 1
    fi
    link="$dest/$skill"
    if [ -L "$link" ] || [ -e "$link" ]; then
      echo "exists: $link"
      continue
    fi
    # Junctions on Windows Git Bash: prefer relative symlink when possible.
    run ln -s "$src" "$link"
    echo "linked: $link -> $src"
  done
done
