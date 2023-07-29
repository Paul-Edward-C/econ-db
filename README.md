# econ-db

- ## Onboard documentation
- ### Cleaning raw data (remember to `cd` to `app/`)
  1. Naming the new file in the designated format `{country}_{category}_{freq}_raw.csv`, in which all in lower case.<br><br>
  2. `clean_raw_data.py`<br>Command as below:<br> `python3 clean_raw_data.py --category {category} --country {country} --freq {freq} --to_db`<br><br>
  3. `create_data_setting.py`<br>Command as below:<br> `python3 clean_raw_data.py --category {category} --country {country} --freq {freq}`<br><br>
  4. `match_mapping.py`<br>Command as below:<br> `python3 match_mapping.py --category {category} --country {country} --freq {freq} --to_db --to_output`<br><br>
- ### Variable definitions
  1. `--category`<br> `export`, `gdp` for now
  2. `--country`<br> `TW`, `CN`, `JP`, `KR` for now
  3. `--freq`<br> `M`, `Q` for now