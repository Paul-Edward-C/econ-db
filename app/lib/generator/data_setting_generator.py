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


def create_data_setting_pipeline(category, country, freq, to_db):
    tool = Tool()
    setting = Setting()

    category_full = setting.category_full_name_map[category]
    freq_full = setting.freq_structure_map[freq]

    data_path = setting.structure[country][category_full][f"{freq_full}_data_path"]
    data = pd.read_csv(data_path, index_col=[0])
    mapping_template_path = setting.category_structure[category_full]["input_path"]
    mapping_template = pd.read_excel(mapping_template_path, index_col=None)

    columns = data.columns.tolist()
    data_setting = pd.DataFrame()

    data_setting = create_chart_type(columns, data_setting)
    data_setting = create_data_type(columns, data_setting)
    data_setting = create_display_name(columns, data_setting, country)

    data_setting.index.name = "name"
    data_setting = data_setting[["display_name", "data_type", "chart_type"]]

    if to_db:
        output_path = setting.structure[country][category_full][f"{freq_full}_setting_path"]
        data_setting.to_csv(output_path, index=True)
    return


def create_chart_type(columns, data_setting):
    col_name = "chart_type"
    for column in columns:
        if "contribution to" in column.lower():
            # logging.warning(f"Contribution column detected: {column}")
            data_setting.loc[column, col_name] = "bar"

        else:
            data_setting.loc[column, col_name] = "line"

    return data_setting


def create_data_type(columns, data_setting):
    col_name = "data_type"

    for column in columns:
        if "%" in column.lower():
            data_setting.loc[column, col_name] = "p"
        else:
            data_setting.loc[column, col_name] = "r"

    return data_setting


def create_display_name(columns, data_setting, country):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category")
    parser.add_argument("--country")
    parser.add_argument("--freq")
    parser.add_argument("--to_db", action="store_true")
    args = parser.parse_args()

    category_list = args.category.split(",") if args.category is not None else None
    country_list = args.country.split(",") if args.country is not None else None
    freq_list = args.freq.split(",") if args.freq is not None else None

    successful_number = 0
    failed_number = 0
    for category in category_list:
        for country in country_list:
            for freq in freq_list:
                try:
                    create_data_setting_pipeline(category, country, freq, to_db=args.to_db)
                    logging.info(
                        f"Successfully create data setting pipeline for category: {category}, country: {country}, freq"
                    )
                    successful_number += 1
                except KeyError as e:
                    logging.error(f"Request data not found for category: {category}, country: {country}, freq: {freq}")
                    failed_number += 1

    logging.info(f"Successfully create {successful_number} data setting pipeline")
    logging.info(f"Failed to create {failed_number} data setting pipeline")


if __name__ == "__main__":
    main()
