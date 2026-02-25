#!/bin/bash
# Run after GitHub repos exist (create via script with GITHUB_TOKEN or manually).
# Repos: konradciok/new-tours-mar26 (root), konradciok/new-tours-mar26-backend (backend).
# Frontend already: konradciok/heritage-travels.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
GITHUB_USER="${GITHUB_USER:-konradciok}"
ROOT_REPO_URL="git@github.com:${GITHUB_USER}/new-tours-mar26.git"
BACKEND_REPO_URL="git@github.com:${GITHUB_USER}/new-tours-mar26-backend.git"
FRONTEND_REPO_URL="git@github.com:${GITHUB_USER}/heritage-travels.git"

echo "==> 1. Push backend to its repo (repo must already exist)..."
cd "$ROOT/backend"
git remote remove origin 2>/dev/null || true
git remote add origin "$BACKEND_REPO_URL"
git push -u origin main

echo "==> 2. Push frontend so origin is in sync..."
cd "$ROOT/frontend"
git push origin main || true

echo "==> 3. In root: remove backend and frontend from index..."
cd "$ROOT"
git rm -r --cached backend 2>/dev/null || true
git rm --cached frontend 2>/dev/null || true

echo "==> 4. Move dirs aside so submodule add can create them..."
mv backend backend_bak
mv frontend frontend_bak

echo "==> 5. Add backend and frontend as submodules..."
git submodule add "$BACKEND_REPO_URL" backend
git submodule add "$FRONTEND_REPO_URL" frontend

echo "==> 6. Remove backups (content is in submodules now)..."
rm -rf backend_bak frontend_bak

echo "==> 7. Commit submodule setup..."
git add .gitmodules backend frontend
git commit -m "Convert backend and frontend to git submodules" || true

echo "==> 8. Add root remote and push..."
git remote remove origin 2>/dev/null || true
git remote add origin "$ROOT_REPO_URL"
git push -u origin main

echo "Done. Root: $ROOT_REPO_URL with submodules backend and frontend."
git submodule status
