import argparse
import logging

from lib.generator.data_setting_generator import Data_Setting_Generator

logging.basicConfig(level=logging.INFO)


def run_create_data_setting_pipeline(category, country, freq, to_db=False):
    generator = Data_Setting_Generator()
    generator.create(category, country, freq, to_db=to_db)


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
                    run_create_data_setting_pipeline(category, country, freq, to_db=args.to_db)
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
