import argparse
import logging

from lib.matcher.export_matcher import Export_matcher
from lib.matcher.gdp_matcher import GDP_matcher
from lib.tools import Setting

logging.basicConfig(level=logging.INFO)


def run_matching_pipeline(category_list, country_list, freq_list, to_db=False, to_output=False):
    setting = Setting()
    matcher_map = {"gdp": GDP_matcher(), "export": Export_matcher()}
    category_list = matcher_map.keys() if category_list is None else category_list

    for category in category_list:
        category_full = setting.category_full_name_map[category]
        freq_country_map = {
            "M": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("M", False)],
            "Q": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("Q", False)],
            "A": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("A", False)],
        }

        matcher = matcher_map[category]

        freq_list = freq_country_map.keys() if freq_list is None else freq_list
        for freq in freq_list:
            current_country_list = (
                freq_country_map[freq]
                if country_list is None
                else [i for i in country_list if i in freq_country_map[freq]]
            )
            for country in current_country_list:
                matching_num, data_num, mapping_length, matching_ratio = matcher.match(
                    country=country, freq=freq, to_db=to_db, to_output=to_output
                )
                logging.info(
                    f"matching_num: {str(matching_num)}, data_num: {data_num}, "
                    f"mapping_length: {str(mapping_length)}, matching_ratio: {str(matching_ratio)}"
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category")
    parser.add_argument("--country")
    parser.add_argument("--freq")
    parser.add_argument("--to_db", action="store_true")
    parser.add_argument("--to_output", action="store_true")
    args = parser.parse_args()

    category_list = args.category.split(",") if args.category is not None else None
    country_list = args.country.split(",") if args.country is not None else None
    freq_list = args.freq.split(",") if args.freq is not None else None
    
    if args.to_db and args.to_output:
        run_matching_pipeline(category_list, country_list, freq_list, args.to_db, args.to_output)
    elif args.to_db:
        run_matching_pipeline(category_list, country_list, freq_list, args.to_db)
    elif args.to_output:
        run_matching_pipeline(category_list, country_list, freq_list, args.to_output)
    else:
        run_matching_pipeline(category_list, country_list, freq_list)
        


if __name__ == "__main__":
    main()
