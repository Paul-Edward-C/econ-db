# =========IMPORT PACKAGES==========
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)")
import pathlib
import sys
from datetime import datetime as dt

import pandas as pd
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting, Tool

# =========DEFINE CLASS OBJECT==========


class Export_matcher:
    def __init__(self, category="export"):
        self.tool = Tool()
        self.setting = Setting()

        self.category = category
        self.category_full = self.setting.category_full_name_map[self.category]

        mapping_template_path = self.setting.category_structure[self.category_full]["input_path"]
        self.mapping_template = pd.read_excel(mapping_template_path, index_col=None)

        value_type_list = list(set(self.mapping_template["Value_type"].dropna().tolist()))
        unit_list = [[g.strip() for g in i.split(",")] for i in self.mapping_template["Unit"].dropna().tolist()]

        self.comb_list = [[i] + j for i in value_type_list for j in unit_list]
        self.comb_component = list(set(item for sublist in self.comb_list for item in sublist))

        self.mapping_path = self.setting.category_structure[self.category_full]["path"]
        self.mapping = pd.read_csv(self.mapping_path, index_col=None)

    def get_fuzz_score(self, str1, str2):
        score = fuzz.token_sort_ratio(str1, str2)
        return score

    def get_cosine_similarity(self, s1, s2):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([s1, s2])
        similarity = cosine_similarity(vectors[0], vectors[1])

        return similarity[0][0]

    def match(self, country, freq, to_db, to_output):
        all_matching_result = pd.DataFrame()
        freq_full = self.setting.freq_full_name_map[freq]
        data_path = self.setting.structure[country][self.category_full][f"{freq_full}_data_path"]
        data = pd.read_csv(data_path, index_col=[0])

        keep_list = [1, 2, 3, 5, 4, 6, 7]

        for index, row in tqdm(
            self.mapping.iterrows(), desc=f"{country}-{freq} matching mapping", unit="mapping object"
        ):
            columns = data.columns

            # Check whether freq of this mapping row is in current matching freq
            if not row[0] in self.setting.freq_data_mapping_map[freq].keys():
                continue

            # Check current mapping comb number

            comb_string = f"{row[2]}, {row[3]}"
            mapping_comb_num = len(comb_string.split(","))

            row = row[~row.isna()]
            mapping_list = [row[i] for i in keep_list if str(i) in row.index.to_list()]

            if len(mapping_list) == 0:
                logging.warning(f"{country}-{freq} mapping row {index} is empty")
                continue

            mapping_list.remove("Total") if "Total" in mapping_list else None

            comb = comb_string
            main_category = row[1]

            mapping_string = ", ".join(mapping_list)

            for i in [main_category, comb]:
                columns = columns[columns.str.lower().str.contains(i.lower())]
            if len(columns) == 0:
                continue

            revised_columns = columns.str.replace(", All", "")
            fuzz_score_list = []
            cos_score_list = []

            matching_columns = []
            for column, revised_column in zip(columns, revised_columns):
                current_comb_list = []
                for comb in self.comb_component:
                    if comb in revised_column:
                        current_comb_list.append(comb)
                current_comb_list = self.tool.remove_duplicated_unit(current_comb_list)
                data_unit_num = len(current_comb_list)
                if data_unit_num != mapping_comb_num:
                    continue

                matching_columns.append(column)
                fuzz_score = self.get_fuzz_score(revised_column, mapping_string) / 100
                cos_score = self.get_cosine_similarity(revised_column, mapping_string)

                fuzz_score_list.append(fuzz_score)
                cos_score_list.append(cos_score)

            matching_result = pd.DataFrame(
                {"data_name": matching_columns, "fuzz_score": fuzz_score_list, "cos_score": cos_score_list}
            ).sort_values(by=["cos_score", "fuzz_score"], ascending=False)
            matching_result = matching_result.loc[
                (matching_result["fuzz_score"] > 0.6) & (matching_result["cos_score"] > 0.5)
            ]

            matching_result["overall_score"] = (matching_result["fuzz_score"] + matching_result["cos_score"]) / 2
            matching_result["mapping_name"] = mapping_string
            matching_result["mapping_index"] = index
            matching_result["matching_length"] = len(matching_result)

            matching_result.index = range(len(all_matching_result), len(all_matching_result) + len(matching_result))

            all_matching_result = pd.concat([all_matching_result, matching_result], axis=0)

        duplicated_data_name_u = all_matching_result[all_matching_result["data_name"].duplicated()][
            "data_name"
        ].unique()
        for duplicate in duplicated_data_name_u:
            duplicate_df = all_matching_result.loc[all_matching_result["data_name"] == duplicate].sort_values(
                by="overall_score", ascending=False
            )
            all_matching_result.drop(duplicate_df.index[1:], inplace=True)

        duplicated_mapping_name_u = all_matching_result[all_matching_result["mapping_name"].duplicated()][
            "mapping_name"
        ].unique()
        for duplicate in duplicated_mapping_name_u:
            duplicate_df = all_matching_result.loc[all_matching_result["mapping_name"] == duplicate].sort_values(
                by="overall_score", ascending=False
            )
            all_matching_result.drop(duplicate_df.index[1:], inplace=True)

        self.mapping.loc[all_matching_result["mapping_index"], country] = all_matching_result["data_name"].tolist()

        if to_db:
            self.mapping.to_csv(self.mapping_path, index=False)

        if to_output:
            output_path = (
                f"db/{country.lower()}/{self.category}/{freq}/"
                f"{dt.today().strftime('%Y%m%d')}_{country}_{self.category}_output.xlsx"
            )

            all_matching_result.to_excel(output_path, index=False)
            pass

        # Create return result values
        matching_num = len(all_matching_result["data_name"].dropna())
        data_num = len(data.columns)
        mapping_length = len(self.mapping)
        matching_ratio = matching_num / data_num

        return matching_num, data_num, mapping_length, matching_ratio
