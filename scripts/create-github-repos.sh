#!/bin/bash
# Create GitHub repos for root and backend (run once, then use git steps).
# Usage: GITHUB_TOKEN=ghp_xxx ./scripts/create-github-repos.sh
# Or create manually: https://github.com/new (new-tours-mar26, new-tours-mar26-backend)

set -e
USER="${GITHUB_USER:-konradciok}"
ROOT_REPO="new-tours-mar26"
BACKEND_REPO="new-tours-mar26-backend"

[ -z "$GITHUB_TOKEN" ] && [ -f "$HOME/.github-token" ] && GITHUB_TOKEN=$(cat "$HOME/.github-token")
if [ -z "$GITHUB_TOKEN" ]; then
  echo "No GITHUB_TOKEN (or ~/.github-token). Create repos manually:"
  echo "  1. https://github.com/new?name=$ROOT_REPO"
  echo "  2. https://github.com/new?name=$BACKEND_REPO"
  exit 0
fi

for name in "$BACKEND_REPO" "$ROOT_REPO"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos -d "{\"name\":\"$name\",\"private\":false}")
  if [ "$code" = "201" ]; then
    echo "Created https://github.com/$USER/$name"
  elif [ "$code" = "422" ]; then
    echo "Repo $name already exists."
  else
    echo "Failed to create $name (HTTP $code)"
    exit 1
  fi
done
