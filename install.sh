#!/usr/bin/env bash
# install.sh — install bmad-samd-qms skills to ~/.claude/skills/
# Usage:
#   ./install.sh            # install globally to ~/.claude/skills/
#   ./install.sh --uninstall  # remove installed skills

set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS=("qms-init" "qms-update")

uninstall() {
  echo "Uninstalling bmad-samd-qms skills..."
  for skill in "${SKILLS[@]}"; do
    target="${SKILLS_DIR}/${skill}"
    if [ -d "$target" ]; then
      rm -rf "$target"
      echo "  removed: ${target}"
    else
      echo "  not found (skipping): ${target}"
    fi
  done
  echo "Done."
}

install() {
  mkdir -p "$SKILLS_DIR"
  echo "Installing bmad-samd-qms skills to ${SKILLS_DIR}/"
  for skill in "${SKILLS[@]}"; do
    src="${PLUGIN_DIR}/skills/${skill}"
    target="${SKILLS_DIR}/${skill}"
    if [ -d "$target" ]; then
      echo "  updating: ${target}"
      rm -rf "$target"
    else
      echo "  installing: ${target}"
    fi
    cp -r "$src" "$target"
  done
  echo ""
  echo "Done. Skills available in every Claude Code session:"
  for skill in "${SKILLS[@]}"; do
    echo "  /${skill}"
  done
  echo ""
  echo "Start a new project with:  /qms-init"
}

if [ "${1:-}" = "--uninstall" ]; then
  uninstall
else
  install
fi
