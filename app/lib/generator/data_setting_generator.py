import pathlib
import sys

import pandas as pd

sys.path.append(f"""{pathlib.Path(__file__).resolve().parent}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting


class Data_Setting_Generator:
    def __init__(self):
        self.setting = Setting()

    def create(self, category, country, freq, to_db):
        print("how")
        freq_full = self.setting.freq_full_name_map[freq]
        print(freq_full)

        raw_data_path = self.setting.structure[country][category][f"{freq_full}_data_path"]
        print(raw_data_path)
        temp_data_setting_path = self.setting.structure[country][category][f"{freq_full}_temp_setting_path"]
        print(temp_data_setting_path)
        data = pd.read_csv(raw_data_path, index_col=[0])
        print(data)
        temp_setting = pd.read_csv(temp_data_setting_path, index_col=None).set_index("cleaned_name")
        print(temp_setting)

        columns = data.columns.tolist()
        data_setting = pd.DataFrame()

        data_setting = self.create_chart_type(columns, data_setting)
        data_setting = self.create_data_type(columns, data_setting, temp_setting=temp_setting)
        data_setting = self.create_display_name(columns, data_setting, country)

        data_setting.index.name = "name"
        data_setting = data_setting[["display_name", "data_type", "chart_type"]]

        if to_db:
            output_path = self.setting.structure[country][category][f"{freq_full}_setting_path"]
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

    def create_data_type(self, columns, data_setting, temp_setting):
        col_name = "data_type"

        for column in columns:
            # len(temp_setting.loc[column] might not be 1)
            try:
                data_setting.loc[column, col_name] = temp_setting.loc[[column]]["data_type"].tolist()[0]
            except KeyError as e:
                data_setting.loc[column, col_name] = "None"

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
