#!/usr/bin/env bash
set -euo pipefail

PROFILE="codex"
TARGET="codex"
APPLY=0
AW_HOME_ARG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    --aw-home)
      AW_HOME_ARG="$2"
      shift 2
      ;;
    --apply)
      APPLY=1
      shift
      ;;
    -h|--help)
      echo "Usage: ./install.sh [--profile base|codex|just-ddl|full] [--target codex|claude-code|all] [--aw-home PATH] [--apply]"
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

python -m pip install -e .

MANIFEST="$ROOT/agentworkos.toml"
python -m agentworkos.cli doctor --manifest "$MANIFEST" --profile "$PROFILE"

SYNC_ARGS=(sync --manifest "$MANIFEST" --target "$TARGET" --profile "$PROFILE")
if [[ -n "$AW_HOME_ARG" ]]; then
  SYNC_ARGS+=(--aw-home "$AW_HOME_ARG")
fi
if [[ "$APPLY" == "1" ]]; then
  SYNC_ARGS+=(--apply)
fi

python -m agentworkos.cli "${SYNC_ARGS[@]}"
