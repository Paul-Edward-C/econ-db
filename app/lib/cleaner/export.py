import argparse
import logging
import pathlib
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO)

sys.path.append(f"""{pathlib.Path(__file__).resolve().parent}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent)}""")
sys.path.append(f"""{str(pathlib.Path(__file__).resolve().parent.parent.parent)}""")
from lib.tools import Setting, Tool


def run_cleaning_pipeline(country, freq, to_db):
    setting = Setting()
    tool = Tool()

    freq_full = setting.freq_full_name_map[freq]
    raw_data_path = setting.structure[country]["Foreign Trade"][f"{freq_full}_raw_data_path"]
    data_path = setting.structure[country]["Foreign Trade"][f"{freq_full}_data_path"]
    data = pd.read_csv(raw_data_path, index_col=[0])
    mapping_template_path = setting.category_structure["Foreign Trade"]["input_path"]
    mapping_template = pd.read_excel(mapping_template_path, index_col=None)

    # Create unique unite list
    value_type_list = list(set(mapping_template["Value_type"].dropna().tolist()))
    unit_list = [[g.strip() for g in i.split(",")] for i in mapping_template["Unit"].dropna().tolist()]

    comb_list = [[i] + j for i in value_type_list for j in unit_list]
    unit_component = list(set(item for sublist in comb_list for item in sublist))

    columns = data.columns.tolist()

    # turn {currency} into LCU
    currencies = setting.country_currency_map[country]
    currency_replace_num = 0

    for currency in currencies:
        new_columns = []
        for column in columns:
            if currency in column:
                new_currency = setting.country_currency_map[country][currency]
                new_column = (
                    column.replace(f"{currency} bn", new_currency)
                    .replace(f"{currency} m", new_currency)
                    .replace(currency, new_currency)
                )

                if new_column != column:
                    currency_replace_num += 1
                column = new_column

            new_columns.append(column)
        columns = new_columns

    # Deal with countries exceptions
    if country == "JP" and freq == "M":
        columns = jp_m_exception(columns, comb_list)
    elif country == "CN" and freq == "M":
        columns = cn_m_exception(columns)
    elif country == "TW" and freq == "M":
        columns = tw_m_exception(columns)
    elif country == "KR" and freq == "M":
        columns = kr_m_exception(columns)

    # Check unit order
    unit_replace_num = 0
    new_columns = []
    ignore_list = ["3mma", "MoM chg", "3m/3m", "Contribution"]
    for column in columns:
        # Calculate unit number in column
        current_unit_list = []
        for unit in unit_component:
            if unit in column:
                current_unit_list.append(unit)
        current_unit_list = tool.remove_duplicated_unit(current_unit_list)
        unit_num = len(current_unit_list)
        right_uni_order_list = [", ".join(units).strip(", ") for units in comb_list if len(units) == unit_num]

        if not any(i in column for i in right_uni_order_list):
            cond_dict = {
                0: {},
                1: {},
                2: {
                    "USD, Value": "Value, USD",
                    "index, Volume": "Volume, index",
                    "% of total, Value": "Value, % of total",
                    "LCU, Value": "Value, LCU",
                    "% of GDP, Value": "Value, % of GDP",
                },
                3: {
                    "Price, % YoY, index": "Price, index, % YoY",
                    "Value, % YoY, index": "Value, index, % YoY",
                    "% YoY, index, Volume": "Volume, index, % YoY",
                    "LCU, % YoY, Value": "Value, LCU, % YoY",
                    "SA, USD, Value": "Value, USD, SA",
                    "USD, % YoY, Value": "Value, USD, % YoY",
                    "index, SA, Volume": "Volume, index, SA",
                    "SA, index, Volume": "Volume, index, SA",
                    "SA, LCU, Value": "Value, LCU, SA",
                    "SA, % of total, Value": "Value, % of total, SA",
                    "SA, index, Value": "Value, index, SA",
                    "index, % YoY, Volume": "Volume, % YoY, index",
                    "USD, SA, Value": "Value, USD, SA",
                    "LCU, SA, Value": "Value, LCU, SA",
                    "SA, % of GDP, Value": "Value, % of GDP, SA",
                },
                4: {
                    "SA, % MoM, index, Volume": "Volume, index, % MoM, SA",
                    "SA, LCU, % MoM, Value": "Value, LCU, % MoM, SA",
                    "SA, USD, % MoM, Value": "Value, USD, % MoM, SA",
                    "index, SA, % YoY, Volume": "Volume, index, % YoY, SA",
                    "SA, % YoY, index, Volume": "Volume, index, % YoY, SA",
                    "SA, LCU, % YoY, Value": "Value, LCU, % YoY, SA",
                    "SA, USD, % YoY, Value": "Value, USD, % YoY, SA",
                    "SA, index, % YoY, Value": "Value, index, % YoY, SA",
                    "index, % MoM, SA, Volume": "Volume, index, % MoM, SA",
                    "index, % YoY, SA, Volume": "Volume, index, % YoY, SA",
                    "USD, % MoM, SA, Value": "Value, USD, % MoM, SA",
                    "LCU, SA, % MoM, Value": "Value, LCU, % MoM, SA",
                },
                5: {},
            }
            check_list = [i for i in cond_dict[unit_num].keys() if i in column]  # Ideally this list length will be one.
            if len(check_list) == 1:
                column = column.replace(check_list[0], cond_dict[unit_num][check_list[0]])
                unit_replace_num += 1
            else:
                if not any(i in column for i in ignore_list):
                    logging.warning(f"Wrong unit order : {column}  {unit_num}")
        new_columns.append(column)

    columns = new_columns
    data.columns = columns

    if to_db:
        data.to_csv(data_path, index=True)
        logging.info(f"{country} {freq} data written to {data_path}")

    logging.info(f"\nCurrency replace num : {currency_replace_num}")
    logging.info(f"Unit replace num : {unit_replace_num}")
    return


def tw_m_exception(columns):  # Add Value to all data without Value_type
    new_columns = []
    value_type_list = ["Value", "Volume", "Price"]
    for column in columns:
        if not any(i in column for i in value_type_list):
            column += ", Value"
        new_columns.append(column)
    return new_columns


def kr_m_exception(columns):  # Add Value to all data without Value_type
    new_columns = []
    value_type_list = ["Value", "Volume", "Price"]
    for column in columns:
        if not any(i in column for i in value_type_list):
            column += ", Value"
        new_columns.append(column)
    return new_columns


def jp_m_exception(columns, comb_list):
    # Deal with {index} columns
    new_columns = []
    index_unit_replace_num = 0
    for column in columns:
        index_map = {"Value Index": "Value", "Quantum Index": "Volume", "Unit Index": "Price"}
        check_list = [i for i in index_map.keys() if i in column]
        if len(check_list) == 1:
            column = column.replace(check_list[0], index_map[check_list[0]])
            column += ", index"
            index_unit_replace_num += 1

        new_columns.append(column)
    columns = new_columns

    # replace Index to index
    new_columns = []
    upper_index_replace_num = 0
    for column in columns:
        if ", Index" in column:  # Better find another solution to detect upper case "Index"
            column = column.replace(", Index", ", index")
            upper_index_replace_num += 1
        new_columns.append(column)
    columns = new_columns

    # Move Volume place
    new_columns = []
    volume_unit_replace_num = 0  # After to_db all the number here are because they have some unit we ignore
    for column in columns:
        if ", Volume" in column and not any([i in column for i in [", ".join(g) for g in comb_list if "Volume" in g]]):
            column = column.replace(", Volume", "")
            column += ", Volume"
            volume_unit_replace_num += 1
        new_columns.append(column)
    columns = new_columns

    # Add "Value" to column without Value_type
    new_columns = []
    add_value_replace_num = 0
    for column in columns:
        if not ("Volume" in column or "Price" in column or "Value" in column):
            column += ", Value"
            add_value_replace_num += 1
        new_columns.append(column)

    logging.info(f"3 kinds index unit replace num: {index_unit_replace_num}")
    logging.info(f"Upper index replace num: {upper_index_replace_num}")
    logging.info(f"Volume unit replace num: {volume_unit_replace_num}")
    logging.info(f"Add value replace num: {add_value_replace_num}")
    return new_columns


def cn_m_exception(columns):
    new_columns = []
    # check does data contain "Value, "Volume" or "Price"
    for column in columns:
        if not ("Value" in column or "Volume" in column or "Price" in column):
            column += ", Value"
        new_columns.append(column)
    return new_columns


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country")  # in upper class
    parser.add_argument("--freq")  # in upper class
    parser.add_argument("--to_db", action="store_true")  # if true, renew results to DB
    args = parser.parse_args()

    country_list = args.country.split(",") if args.country is not None else None
    freq_list = args.freq.split(",") if args.freq is not None else None

    for country in country_list:
        for freq in freq_list:
            run_cleaning_pipeline(country, freq, args.to_db)


if __name__ == "__main__":
    main()
