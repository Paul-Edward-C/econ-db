import logging
import pathlib

import pandas as pd

logging.basicConfig(level=logging.INFO)
import sys

sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting, Tool


class GDP_cleaner:
    def __init__(self):
        self.setting = Setting()
        self.tool = Tool()
        mapping_template_path = self.setting.category_structure["National Accounts"]["input_path"]
        self.mapping_template = pd.read_excel(mapping_template_path, index_col=None)

    def clean(self, country, freq, to_db):
        logging.info(f"Running cleaning pipeline for GDP-{country}-{freq}")

        freq_full = self.setting.freq_full_name_map[freq]
        raw_data_path = self.setting.structure[country]["National Accounts"][f"{freq_full}_raw_data_path"]
        temp_data_setting_path = self.setting.structure[country]["National Accounts"][f"{freq_full}_temp_setting_path"]
        data_path = self.setting.structure[country]["National Accounts"][f"{freq_full}_data_path"]
        data = pd.read_csv(raw_data_path, index_col=[0])
        temp_data_setting = pd.read_csv(temp_data_setting_path, index_col=[0])

        # Create unique unit components
        unit_list = [[g.strip() for g in i.split(",")] for i in self.mapping_template["Unit"].dropna().tolist()]
        unit_component = list(set(item for sublist in unit_list for item in sublist))

        columns = data.columns.tolist()

        # turn XXX into LCU
        currencies = self.setting.country_currency_map[country]
        currency_replace_num = 0

        for currency in currencies:
            new_columns = []
            for column in columns:
                if currency in column:
                    new_currency = self.setting.country_currency_map[country][currency]
                    new_column = column.replace(f"{currency} bn", new_currency).replace(currency, new_currency)

                    if new_column != column:
                        currency_replace_num += 1
                    column = new_column

                new_columns.append(column)
            columns = new_columns

        # Deal with country exceptions
        if country == "CN" and freq == "Q":
            columns = self.cn_q_exception(columns, unit_component)
        elif country == "KR" and freq == "Q":
            columns = self.kr_q_exception(columns, unit_component)
        elif country == "JP" and freq == "Q":
            columns = self.jp_q_exception(columns, unit_component)
        elif country == "TW" and freq == "Q":
            columns = self.tw_q_exception(columns, unit_component)

        # Check unit order
        unit_replace_num = 0
        new_columns = []
        ignore_list = ["SAAR", "ppt", "YTD"]

        cond_dict = {
            0: {},
            1: {},
            2: {
                "% QoQ, LCU": "LCU, % QoQ",
                "% YoY, LCU": "LCU, % YoY",
                "SA, LCU": "LCU, SA",
                "SA, USD": "USD, SA",
                "SA, % of GDP": "% of GDP, SA",
                "SA, % QoQ": "% QoQ, SA",
                "SA, % YoY": "% YoY, SA",
                "% of GDP, LCU": "LCU, % of GDP",
            },
            3: {
                "Contribution to % YoY chg, ppts, LCU": "LCU, Contribution to % YoY chg, ppts",
                "Contribution to % QoQ chg, ppts, LCU": "LCU, Contribution to % QoQ chg, ppts",
                "% of GDP, SA, LCU": "LCU, % of GDP, SA",
                "% YoY, SA, LCU": "LCU, % YoY, SA",
                "SA, % of GDP, LCU": "LCU, % of GDP, SA",
                "SA, % QoQ, LCU": "LCU, % QoQ, SA",
                "SA, % YoY, LCU": "LCU, % YoY, SA",
                "SA, LCU, % YoY": "LCU, % YoY, SA",
            },
            4: {},
        }

        for column in columns:
            # Calculate unit number in column
            current_unit_list = []
            for unit in unit_component:
                if unit in column:
                    current_unit_list.append(unit)
            current_unit_list = self.tool.remove_duplicated_unit(current_unit_list)
            unit_num = len(current_unit_list)
            right_unit_order_list = [", ".join(units).strip(", ") for units in unit_list if len(units) == unit_num]

            if not any(i in column for i in right_unit_order_list):
                check_list = [
                    i for i in cond_dict[unit_num].keys() if i in column
                ]  # Ideally this list length will be one.
                if len(check_list) == 1:
                    column = column.replace(check_list[0], cond_dict[unit_num][check_list[0]])
                    unit_replace_num += 1
                else:
                    if not (any(i in column for i in ignore_list)):
                        logging.warning(f"Wrong unit order : {column}  {unit_num} {current_unit_list} {check_list}")

            new_columns.append(column)
        columns = new_columns

        # Write raw data name and new column name into temp data_setting_file
        for column, new_column in zip(data.columns, columns):
            temp_data_setting.loc[column, "cleaned_name"] = new_column
        temp_data_setting.to_csv(temp_data_setting_path, index=True)

        data.columns = columns
        if to_db:
            data.to_csv(data_path, index=True)

        logging.info(f"Currency replace num : {currency_replace_num}")
        logging.info(f"Unit replace num : {unit_replace_num}\n")
        return

    def tw_q_exception(self, columns, unit_component):  # Add LCU unit to column not have currency unit
        new_columns = []

        currency_units = ["LCU", "USD"]
        for column in columns:
            if not any(i in column for i in currency_units):
                column += ", LCU"

            new_columns.append(column)
        return new_columns

    def jp_q_exception(self, columns, unit_component):  # Add LCU unit to column not have currency unit
        new_columns = []

        currency_units = ["LCU", "USD"]
        for column in columns:
            if not any(i in column for i in currency_units):
                column += ", LCU"

            new_columns.append(column)
        columns = new_columns

        new_columns = []
        for column in columns:
            if "SA % QoQ" in column:
                column = column.replace("SA % QoQ", "SA, % QoQ")
            new_columns.append(column)

        return new_columns

    def cn_q_exception(self, columns, unit_component):  # Add LCU unit to column only with % YoY or % QoQ
        tool = Tool()
        new_columns = []

        for column in columns:
            unit_list = []
            for unit in unit_component:
                if unit in column:
                    unit_list.append(unit)
            unit_list = tool.remove_duplicated_unit(unit_list)
            unit_num = len(unit_list)
            if unit_num == 1 and (unit_list[0] == "% YoY" or unit_list[0] == "% QoQ"):
                column = column + ", LCU"

            elif unit_num == 2 and (
                "ppts" in unit_list
                and ("Contribution to % YoY chg" in unit_list or "Contribution to % QoQ chg" in unit_list)
            ):
                column = column + ", LCU"

            new_columns.append(column)

        return new_columns

    def kr_q_exception(self, columns, unit_component):  # Add LCU unit to column without currency unit
        tool = Tool()
        new_columns = []

        currency_units = ["LCU", "USD"]
        for column in columns:
            if not any(i in column for i in currency_units):
                column += ", LCU"
            new_columns.append(column)

        return new_columns
