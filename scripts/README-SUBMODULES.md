# Root repo with backend/frontend submodules (git only)

Goal: one GitHub repo at root with `backend` and `frontend` as git submodules.

## 1. Create GitHub repos (no `gh` CLI)

**Option A – with token (git only, no `gh`):**
```bash
export GITHUB_TOKEN=ghp_xxxx   # from GitHub Settings → Developer settings → Personal access tokens
./scripts/create-github-repos.sh
```

**Option B – manual:** Create two empty repos on GitHub:
- [new-tours-mar26](https://github.com/new?name=new-tours-mar26) (root)
- [new-tours-mar26-backend](https://github.com/new?name=new-tours-mar26-backend) (backend)

Frontend already lives at `konradciok/heritage-travels`.

## 2. Run submodule setup and push (git only)

```bash
./scripts/setup-submodules-and-push.sh
```

This will:
- Push `backend` to `new-tours-mar26-backend`
- Sync `frontend` to `heritage-travels`
- Remove `backend` and `frontend` from root’s index and add them as submodules
- Add root remote and push to `new-tours-mar26`

## If push doesn’t work (e.g. SSH blocked): use tunnel or HTTPS

- **HTTPS instead of SSH:** In the script, change URLs to  
  `https://github.com/konradciok/REPO.git` and push; use a token or credential helper when prompted.
- **SSH over a tunnel:** If you use an SSH tunnel to reach GitHub, ensure `GIT_SSH_COMMAND` or your `~/.ssh/config` uses that tunnel before running the script.

## After setup

- Clone root with submodules: `git clone --recurse-submodules git@github.com:konradciok/new-tours-mar26.git`
- Or in an existing clone: `git submodule update --init --recursive`
