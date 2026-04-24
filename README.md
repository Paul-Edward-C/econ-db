

## econ-db

Bokeh app deployed on Heroku (`econ-db-0f18c1ac664a.herokuapp.com`). Heroku builds from `main`.

### Updating the app (routine data refresh)

One command does the whole loop — loader → commit → push → PR.

```bash
econ-db-update                          # commit message defaults to "Data update YYYY-MM-DD"
econ-db-update "Refresh KR + JP data"   # or supply your own
```

What it does:

1. Refuses to run only if there are uncommitted changes **outside `app/db/`** (prints the offending files — clean them up first). Raw-CSV changes under `app/db/` are expected and carried into the new branch.
2. Fetches `origin`, switches to `main`, fast-forwards.
3. Creates `data-update-YYYY-MM-DD` (appends `-HHMM` if that branch already exists, so same-day reruns work).
4. Runs `app/load_new_v2.py`.
5. If the loader produced changes: `git add .`, commit, push, open PR against `main`, print the PR URL.
6. If no changes: deletes the empty branch and exits. No empty PR.
7. If the loader errors: deletes the empty branch, surfaces the exit code, leaves `git` untouched.

Before the first run:
- Drop the updated `*_raw.csv` files into `app/db/{country}/{category}/{freq}/` (see onboarding below for filename/folder rules).
- Make sure `gh` is installed and authenticated (`gh auth status`).
- The alias lives in `~/.zshrc` — open a new terminal tab, or `source ~/.zshrc`, if `type econ-db-update` doesn't resolve.

Equivalent without the alias:

```bash
~/Documents/ghost/econ-db/scripts/update_and_pr.sh ["commit message"]
```

Troubleshooting:
- **Loader fails** → `cd app && python load_new_v2.py` to see the full traceback.
- **Script refuses to start ("uncommitted changes outside app/db/")** → you have in-flight script/config edits. Commit, `git stash`, or `git restore .` the listed files, then rerun. Raw-CSV dirt under `app/db/` is fine.
- **PR opens with an unexpected diff** → `git log --oneline main..HEAD`; if the base is stale, make sure `origin/main` is current before rerunning.

Full walk-through in `scripts/README.md`.

### NEW ONBOARDING INSTRUCTIONS
  1. Name your new data file in the format of `{country}_{category}_{freq}_raw_new.csv`, for example, `tw_gdp_q_raw_new.csv`.
  2. Place your new data file in the relevant folder, for instance the example above would go in `db\tw\gdp\q`
  3. Run the python file locally in a bash terminal from `...\GitHub\econ-db\app>` using `python load_new.py`, any files found named with `_new.csv` at the end will automatically be onboarded.

- ### Onboarding documentation
  1. Name the file in the format of `{country}_{category}_{freq}_raw.csv`, for example, `tw_gdp_q_raw.csv`.
  2. Use the following command to clean the raw data and match the data with the mapping, remember to replace the arguments with the file you updated.
    ```bash
  python3 onboarding_pipeline.py --category gdp --country TW --freq Q --to_db --to_output
  ```
- ### Variable definitions
  1. `--category`<br> `Trade`, `GDP` for now
  2. `--country`<br> `TW`, `CN`, `JP`, `KR` for now
  3. `--freq`<br> `M`, `Q` for now
