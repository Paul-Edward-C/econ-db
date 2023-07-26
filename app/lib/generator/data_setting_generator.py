import pathlib
import sys

import pandas as pd

sys.path.append(f"""{pathlib.Path(__file__).resolve().parent}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting


class Data_Setting_Generator:
    def create(self, category, country, freq, to_db):

        setting = Setting()

        category_full = setting.category_full_name_map[category]
        freq_full = setting.freq_full_name_map[freq]

        raw_data_path = setting.structure[country][category_full][f"{freq_full}_data_path"]
        data = pd.read_csv(raw_data_path, index_col=[0])

        columns = data.columns.tolist()
        data_setting = pd.DataFrame()

        data_setting = self.create_chart_type(columns, data_setting)
        data_setting = self.create_data_type(columns, data_setting)
        data_setting = self.create_display_name(columns, data_setting, country)

        data_setting.index.name = "name"
        data_setting = data_setting[["display_name", "data_type", "chart_type"]]

        if to_db:
            output_path = setting.structure[country][category_full][f"{freq_full}_setting_path"]
            data_setting.to_csv(output_path, index=True)
        return

    def create_chart_type(self, columns, data_setting):
        col_name = "chart_type"
        for column in columns:
            if "contribution to" in column.lower():
                # logging.warning(f"Contribution column detected: {column}")
                data_setting.loc[column, col_name] = "bar"

            else:
                data_setting.loc[column, col_name] = "line"

        return data_setting

    def create_data_type(self, columns, data_setting):
        col_name = "data_type"

        for column in columns:
            if "%" in column.lower():
                data_setting.loc[column, col_name] = "p"
            else:
                data_setting.loc[column, col_name] = "r"

        return data_setting

    def create_display_name(self, columns, data_setting, country):
        col_name = "display_name"
        for column in columns:
            if data_setting.loc[column, "data_type"] == "r":
                data_setting.loc[
                    column, col_name
                ] = f"{country}, {column}, bn"  # bn is temporary, after add more data will need a
                # function top determine value display_name
            else:
                data_setting.loc[column, col_name] = f"{country}, {column}"

        return data_setting
