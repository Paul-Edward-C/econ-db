# =========IMPORT PACKAGES==========
import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO)

sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")

from datetime import datetime as dt

import numpy as np
import pandas as pd

pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option("display.max_rows", 3000)
pd.set_option("display.max_columns", 3000)
from fuzzywuzzy import fuzz
from lib.tools import Setting, Tool
from tqdm import tqdm

# =========DEFINE CLASS OBJECT==========


class GDP_matcher:
    def __init__(self, category="gdp"):
        self.tool = Tool()
        self.setting = Setting()

        self.category = category
        self.category_full = self.setting.category_full_name_map[self.category]

        mapping_template_path = self.setting.category_structure[self.category_full]["input_path"]
        self.mapping_template = pd.read_excel(mapping_template_path, index_col=None)
        unit_list = [[g.strip() for g in i.split(",")] for i in self.mapping_template["Unit"].dropna().tolist()]
        self.unit_component = list(set(item for sublist in unit_list for item in sublist))

        self.mapping_path = self.setting.category_structure[self.category_full]["path"]
        self.mapping = pd.read_csv(self.mapping_path, index_col=None)

    def get_similarity_score(self, str1, str2):
        score = fuzz.token_sort_ratio(str1, str2)
        return score

    def run_matching_pipeline(self, country, freq, to_db, to_output):  # one country, one freq per matching.
        freq_full = self.setting.freq_full_name_map[freq]
        data_path = self.setting.structure[country][self.category_full][f"{freq_full}_data_path"]
        data = pd.read_csv(data_path, index_col=[0])

        keep_list = [0, 3, 4, 5, 6, 7, 8, 1]

        matching_result = pd.DataFrame()
        matching_result_columns = ["mapping_name", "data_name", "valid_number", "score", "mapping_index"]

        for index, row in tqdm(
            self.mapping.iterrows(), desc=f"{country}-{freq} matching mapping", unit="mapping object"
        ):
            columns = data.columns

            # Check whether freq of this mapping row is in current matching freq
            if not row[0] in self.setting.freq_data_mapping_map[freq].keys():
                continue

            # Check current mapping unit number
            mapping_unit_num = len(row[1].split(","))

            # Get current mapping list in order
            row = row[~row.isna()]
            mapping_list = [row[i] for i in keep_list if str(i) in row.index.to_list()]

            if len(mapping_list) == 0:
                logging.warning(f"{country}-{freq} mapping row {index} is empty")
                continue

            mapping_list.remove("Total") if "Total" in mapping_list else None

            unit = row[1]
            main_category = self.setting.freq_data_mapping_map[freq][row[0]]
            mapping_list[0] = main_category
            mapping_str = ", ".join(mapping_list)

            # exclude data without main category and unit in its name
            for i in [main_category, unit]:
                columns = columns[columns.str.contains(i)]
            if len(columns) == 0:
                matching_result.loc[len(matching_result), matching_result_columns] = [mapping_str, np.nan, 0, 0, np.nan]
                continue

            # Deal with country exceptions

            # Start find column with highest similarity score
            max_score = 0
            max_score_data_name = ""
            valid_number = len(columns)
            for column in columns:
                current_unit_list = []
                for unit in self.unit_component:
                    if unit in column:
                        current_unit_list.append(unit)
                current_unit_list = self.tool.remove_duplicated_unit(current_unit_list)
                data_unit_num = len(current_unit_list)

                if data_unit_num != mapping_unit_num:
                    valid_number -= 1
                    continue

                score = self.get_similarity_score(column, mapping_str)
                if score > max_score:
                    max_score = score
                    max_score_data_name = column

            matching_result.loc[len(matching_result), matching_result_columns] = [
                mapping_str,
                max_score_data_name,
                valid_number,
                max_score / 100,
                index,
            ]

        # Remove multiple mapping references are same column condition => only keep the mapping row with higher score
        all_match_data_names = matching_result["data_name"].unique().tolist()
        for i in all_match_data_names:
            filtered_matching = matching_result.loc[matching_result["data_name"] == i]
            if len(filtered_matching) > 1:
                drop_index_list = filtered_matching.sort_values(by="score", ascending=False).index.tolist()[1:]
                for index in drop_index_list:
                    matching_result.loc[index, ["data_name", "score", "valid_number", "mapping_index"]] = [
                        np.nan,
                        0,
                        0,
                        np.nan,
                    ]

        if to_output:
            output_path = (
                f"db/{country.lower()}/{self.category}/{freq.lower()}/"
                f"{dt.today().strftime('%Y%m%d')}_{country}_{self.category}_output.xlsx"
            )
            matching_result = matching_result.loc[~matching_result["data_name"].isna()]
            matching_result.to_excel(output_path, index=False)

        if to_db:
            # write result to db
            for _, row in matching_result.iterrows():
                self.mapping.loc[row["mapping_index"], country] = row["data_name"]
                self.mapping.dropna(how="all", axis=0, inplace=True)
            self.mapping.to_csv(self.mapping_path, index=False)

        # Create return result values
        matching_num = len(matching_result["data_name"].dropna())
        data_num = len(data.columns)
        mapping_length = len(self.mapping)
        matching_ratio = matching_num / data_num

        return matching_num, data_num, mapping_length, matching_ratio
