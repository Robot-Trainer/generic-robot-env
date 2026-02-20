#!/usr/bin/env bash
# More resilient script for counting cameras
# This avoids closing the shell if sourced and follows symbolic links in subdirectories.

# Use a default root if no argument is provided
DEFAULT_ROOT="/home/bernie/code/gym_hil_generator/mujoco_menagerie"
ROOT_DIR="${1:-$DEFAULT_ROOT}"

if [ ! -d "$ROOT_DIR" ]; then
  echo "Directory not found: $ROOT_DIR" >&2
  # Use return if sourced to avoid closing terminal, otherwise exit
  (return 0 2>/dev/null) && return 1 || exit 1
fi

total=0
# Print header
printf '%-80s %s\n' "file" "count"
printf '%-80s %s\n' "--------------------------------------------------------------------------------" "-----"

# Use find -L to follow symbolic links and ensure we look into all subdirectories
# find -print0 handles filenames with spaces safely
while IFS= read -r -d '' file; do
  # Count literal occurrences of '<camera' in each file
  # grep -o outputs each match on a new line; wc -l counts those lines
  count=$(grep -o '<camera' "$file" 2>/dev/null | wc -l || true)
  if [ "$count" -gt 0 ]; then
    printf '%-80s %d\n' "$file" "$count"
    total=$((total + count))
  fi
done < <(find -L "$ROOT_DIR" -type f -name '*.xml' -print0)

echo
printf 'Total occurrences of "<camera" in %s: %d\n' "$ROOT_DIR" "$total"
