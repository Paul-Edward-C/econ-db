import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO)

import pandas as pd

sys.path.append(f"""{pathlib.Path(__file__).resolve().parent}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting

"""
This generator is used to generate number of different raw data (billion/million/thousand) and export the raw data name
and number unit to a temp file and that file will be used when creating data setting files.
"""


class Number_Unit_Generator(object):
    def __init__(self):
        self.setting = Setting()
        pass

    def create(self, category, country, freq):
        category_full = self.setting.category_full_name_map[category]
        freq_full = self.setting.freq_full_name_map[freq]
        raw_data_path = self.setting.structure[country][category_full][f"{freq_full}_raw_data_path"]
        output_path = self.setting.structure[country][category_full][f"{freq_full}_temp_setting_path"]

        raw_data = pd.read_csv(raw_data_path, parse_dates=True, index_col=[0])

        # Use to determine raw data number unit
        number_unit_data_type_map = {
            "k": [],
            "b": ["JPY bn", "NTD bn", "USD bn", "KRW bn", "CNY bn", "TWD bn"],
            "m": [],
            "p": [
                "% of GDP",
                "% YoY",
                "% QoQ",
                "Contribution to QoQ chg, ppts",
                "% SAAR",
                "Contribution to YoY chg, ppts",
                "Contribution to YoY % chg, ppts",
                "SA, % MoM",
                "SA, % of total",
                "SA, TWD bn, % MoM",
                "% of total exports",
                "% of total",
                "% of world",
                "Contribution to MoM chg, ppts",
            ],
        }

        result = pd.DataFrame()
        for column in raw_data.columns:
            status_list = [
                any([i in column for i in number_unit_data_type_map[k]]) for k in number_unit_data_type_map.keys()
            ]

            if any(status_list):
                data_types = [unit for unit, status in zip(number_unit_data_type_map.keys(), status_list) if status]
                result.loc[column, "data_type"] = "p" if "p" in data_types and len(data_types) != 1 else data_types[0]
            else:
                result.loc[column, "data_type"] = "None"
                logging.warning(f"No matching:{column}")

        result.reset_index(inplace=True)

        result.columns = ["raw_data_name", "data_type"]
        result.to_csv(output_path, index=False)

        return result
