#!/usr/bin/env bash
# worktree-manager.sh - Ephemeral Git Worktree Manager for Multi-Agent Collaboration
# Part of the 'andyapproach' skill. Author: andylockran
set -euo pipefail

WORKTREE_BASE_DIR=".worktrees"

usage() {
  cat <<EOF
Usage: $0 <command> [arguments]

Commands:
  create <name> [base-branch]   Create a new isolated worktree under ${WORKTREE_BASE_DIR}/<name>
  list                          List all active worktrees
  lock <name> [reason]          Lock a worktree against accidental removal
  unlock <name>                 Unlock a worktree
  remove <name> [--force]       Remove an agent worktree and clean up references
  prune                         Prune stale administrative worktree metadata

Examples:
  $0 create feat-auth main
  $0 list
  $0 remove feat-auth
EOF
  exit 1
}

CMD="${1:-}"
shift || usage

ensure_gitignore() {
  if ! grep -qs "^/${WORKTREE_BASE_DIR}/" .gitignore 2>/dev/null; then
    echo "/${WORKTREE_BASE_DIR}/" >> .gitignore
    echo "Added /${WORKTREE_BASE_DIR}/ to .gitignore"
  fi
}

case "${CMD}" in
  create)
    NAME="${1:-}"
    BASE="${2:-main}"
    [[ -z "${NAME}" ]] && { echo "Error: Missing worktree name."; usage; }
    
    TARGET_DIR="${WORKTREE_BASE_DIR}/${NAME}"
    BRANCH="feat/${NAME}"

    ensure_gitignore
    mkdir -p "${WORKTREE_BASE_DIR}"

    if git worktree list | grep -q "[ /]${TARGET_DIR} "; then
      echo "Worktree '${TARGET_DIR}' already exists."
      exit 0
    fi

    echo "Provisioning worktree: ${TARGET_DIR} on branch ${BRANCH} (from ${BASE})..."
    if git show-ref --quiet "refs/heads/${BRANCH}"; then
      git worktree add "${TARGET_DIR}" "${BRANCH}"
    else
      git worktree add -b "${BRANCH}" "${TARGET_DIR}" "${BASE}"
    fi

    echo "✅ Worktree ready at: $(pwd)/${TARGET_DIR}"
    ;;

  list)
    echo "=== Active Git Worktrees ==="
    git worktree list
    ;;

  lock)
    NAME="${1:-}"
    REASON="${2:-Subagent active task}"
    [[ -z "${NAME}" ]] && { echo "Error: Missing worktree name."; usage; }
    TARGET_DIR="${WORKTREE_BASE_DIR}/${NAME}"
    git worktree lock "${TARGET_DIR}" --reason "${REASON}"
    echo "🔒 Locked ${TARGET_DIR}: ${REASON}"
    ;;

  unlock)
    NAME="${1:-}"
    [[ -z "${NAME}" ]] && { echo "Error: Missing worktree name."; usage; }
    TARGET_DIR="${WORKTREE_BASE_DIR}/${NAME}"
    git worktree unlock "${TARGET_DIR}"
    echo "🔓 Unlocked ${TARGET_DIR}"
    ;;

  remove)
    NAME="${1:-}"
    FORCE="${2:-}"
    [[ -z "${NAME}" ]] && { echo "Error: Missing worktree name."; usage; }
    TARGET_DIR="${WORKTREE_BASE_DIR}/${NAME}"

    if [[ "${FORCE}" == "--force" || "${FORCE}" == "-f" ]]; then
      git worktree remove --force "${TARGET_DIR}" || rm -rf "${TARGET_DIR}"
    else
      git worktree remove "${TARGET_DIR}"
    fi
    git worktree prune
    echo "🗑️  Removed worktree ${TARGET_DIR} and pruned metadata."
    ;;

  prune)
    git worktree prune -v
    echo "✅ Worktrees pruned."
    ;;

  *)
    usage
    ;;
esac
