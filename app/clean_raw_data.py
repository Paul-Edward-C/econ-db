import argparse
import logging

from lib.cleaner.export_cleaner import EXPORT_cleaner
from lib.cleaner.gdp_cleaner import GDP_cleaner
from lib.generator.number_unit_generator import Number_Unit_Generator
from lib.tools import Setting


def run_cleaning_pipeline(category_list, country_list, freq_list, to_db=False):
    setting = Setting()
    cleaner_map = {"gdp": GDP_cleaner(), "export": EXPORT_cleaner()}
    category_list = cleaner_map.keys() if category_list is None else category_list

    for category in category_list:
        category_full = setting.category_full_name_map[category]
        freq_country_map = {
            "M": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("M", False)],
            "Q": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("Q", False)],
            "A": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("A", False)],
        }

        cleaner = cleaner_map[category]
        number_unit_generator = Number_Unit_Generator()

        freq_list = freq_country_map.keys() if freq_list is None else freq_list
        for freq in freq_list:
            current_country_list = (
                freq_country_map[freq]
                if country_list is None
                else [i for i in country_list if i in freq_country_map[freq]]
            )
            for country in current_country_list:
                number_unit_generator.create(country=country, category=category, freq=freq)
                cleaner.clean(country, freq, to_db)
                logging.info(f"Finished cleaning country: {category}-{country}-{freq} to DB: {to_db}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category")  # in under case
    parser.add_argument("--country")  # in upper case
    parser.add_argument("--freq")  # in upper case
    parser.add_argument("--to_db", action="store_true")  # if true, renew results to DB
    args = parser.parse_args()

    category_list = args.category.split(",") if args.category is not None else None
    country_list = args.country.split(",") if args.country is not None else None
    freq_list = args.freq.split(",") if args.freq is not None else None

    if args.to_db:
        run_cleaning_pipeline(category_list, country_list, freq_list, args.to_db)
    else:
        run_cleaning_pipeline(category_list, country_list, freq_list)


if __name__ == "__main__":
    main()
