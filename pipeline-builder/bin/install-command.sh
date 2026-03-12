#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${1:-$HOME/.local/bin}"

mkdir -p "${TARGET_DIR}"
ln -sf "${ROOT_DIR}/bin/pipeline-builder" "${TARGET_DIR}/pipeline-builder"

cat <<MSG
Installed: ${TARGET_DIR}/pipeline-builder

If this directory is not in PATH, add this to ~/.zshrc:
  export PATH="${TARGET_DIR}:\$PATH"

Then run:
  source ~/.zshrc
MSG
