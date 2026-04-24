# scripts/

Automation scripts for maintaining `econ-db`.

## `update_and_pr.sh` — one-shot data refresh + PR

Runs the data loader and opens a pull request against `main` in a single command.

### Usage

```bash
econ-db-update                          # default commit message: "Data update YYYY-MM-DD"
econ-db-update "Refresh KR + JP data"   # custom commit message
```

Or, without the alias:

```bash
./scripts/update_and_pr.sh
./scripts/update_and_pr.sh "Refresh KR + JP data"
```

### What it does, step by step

1. **Guards** — aborts only if there are uncommitted changes **outside `app/db/`** (so in-flight script/config edits can never be swallowed). Dirty files under `app/db/` are expected — that's where raw CSVs are dropped between runs — and are carried into the new branch.
2. **Syncs `main`** — `git fetch origin main`, switches to `main`, fast-forwards. Fails loudly if local `main` has diverged from `origin`.
3. **Creates a new branch** off `main`: `data-update-YYYY-MM-DD`. If that branch name already exists (local or remote), it appends `-HHMM` so same-day reruns still work.
4. **Verifies the loader** exists at `app/load_new_v2.py`.
5. **Runs the loader** (`python load_new_v2.py` inside `app/`). Any non-zero exit deletes the empty branch and surfaces the exit code — `git` state is untouched.
6. **If the loader made changes**: `git add . && git commit -m "<message>"`, `git push -u origin <branch>`, then `gh pr create --base main` and prints the PR URL.
7. **If the loader made no changes**: deletes the empty branch and exits cleanly. No empty PR.

### Prerequisites (one-time setup)

- **`gh` CLI installed and authenticated** with `repo` scope. Check with `gh auth status`.
- **Python with the data-loader's dependencies**. The script calls `python` from `$PATH` — make sure that resolves to the interpreter that has what `load_new_v2.py` needs.
- **Shell alias** (already appended to `~/.zshrc`):
  ```
  alias econ-db-update='~/Documents/ghost/econ-db/scripts/update_and_pr.sh'
  ```
  Activate with `source ~/.zshrc` or just open a new terminal.

### Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ERROR: uncommitted changes outside app/db/ in …` | You have in-flight edits to scripts/config. Commit, stash, or `git restore .` the listed files, then rerun. Raw-CSV changes under `app/db/` don't trigger this. |
| `fatal: Not possible to fast-forward` | Local `main` has commits that aren't on `origin/main`. Investigate manually — this should never happen in the normal data-refresh flow. |
| Loader prints a Python traceback and script exits non-zero | Run `python app/load_new_v2.py` manually inside the repo for the full trace. The script has already cleaned up its branch. |
| `No changes produced by load_new_v2.py` | Expected if the loader already ran recently or there's no new data upstream. No PR is created. |
| Alias `econ-db-update` not found | You're in a shell started before the alias was added. Run `source ~/.zshrc` or open a new terminal. |

### Cleaning up stale branches

After several PRs land you'll accumulate local branches that are already merged into `main`. Prune them with:

```bash
git fetch --prune origin
git branch --merged main \
  | grep -vE '^\*| main$' \
  | xargs -n1 git branch -d
```

`git branch -d` refuses to delete unmerged branches, so this is safe to run anytime.
