

## econ-db

- ### NEW ONBOARDING INSTRUCTIONS
  1. Name your new data file in the format of `{country}_{category}_{freq}_raw_new.csv`, for example, `tw_gdp_q_raw_new.csv`.
  2. Place your new data file in the relevant folder, for instance the example above would go in `db\tw\gdp\q`
  3. Run the application locally in the powershell terminal from `...\GitHub\econ-db>` using `python -m bokeh serve --show app/`, any files found named with `_new` at the end will automatically be onboarded.


- ### THE METHOD BELOW STILL WORKS AS WELL

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
