

## econ-db

- ### Onboarding documentation
  1. Name the file in the format of `{country}_{category}_{freq}_raw.csv`, for example, `tw_gdp_q_raw.csv`.
  2. Use the following command to clean the raw data and match the data with the mapping, remember to replace the arguments with the file you updated.
    ```bash
  python3 onboarding_pipeline.py --category gdp --country TW --freq Q --to_db --to_output
  ```
- ### Variable definitions
  1. `--category`<br> `export`, `gdp` for now
  2. `--country`<br> `TW`, `CN`, `JP`, `KR` for now
  3. `--freq`<br> `M`, `Q` for now
