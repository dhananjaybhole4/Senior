#!/usr/bin/env bash
# Download the external data Senior's research uses into eval/data/ (gitignored). Resumable: rerun to continue.
# 1) SWE-chat (ODC-BY, gated): sessions + conversations tables, 6.5 GB. Needs a Hugging Face read token in
#    ~/.cache/huggingface/token (or $HF_TOKEN) after accepting the dataset terms.
# 2) Misalignment labels from arXiv 2605.29442 (MIT): 16,118 labelled failure episodes, ~37 MB.
set -euo pipefail
DATA="$(dirname "$0")/data"

SWE_REPO="https://huggingface.co/datasets/SALT-NLP/SWE-chat/resolve/main"
SWE_FILES=(sessions.parquet conversations.parquet)
MIS_REPO="https://raw.githubusercontent.com/ND-SaNDwichLAB/coding-agent-misalignment/HEAD/data/core"
MIS_FILES=(annotated_misalignments.json annotated_misalignments_spec.md session_mapping.json
           session_mapping_spec.md validated_misalignments.json validated_misalignments_spec.md)

fetch() {  # dest_dir base_url file [curl args...]
  local dest=$1 url=$2 f=$3; shift 3
  mkdir -p "$dest"; echo "downloading $f"
  curl -fL --retry 5 -C - "$@" -o "$dest/$f" "$url/$f"
}

for f in "${MIS_FILES[@]}"; do fetch "$DATA/misalignment" "$MIS_REPO" "$f"; done
TOKEN="${HF_TOKEN:-$(cat "$HOME/.cache/huggingface/token")}"
for f in "${SWE_FILES[@]}"; do fetch "$DATA/swe-chat" "$SWE_REPO" "$f" -H "Authorization: Bearer $TOKEN"; done
ls -lh "$DATA"/*
