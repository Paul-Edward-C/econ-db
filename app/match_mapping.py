from lib.matcher.export_matcher import Export_matcher
from lib.matcher.gdp_matcher import GDP_matcher
from lib.tools import Setting
from datetime import datetime as dt
import argparse


def match_export(country_list, freq_list, category):
    setting = Setting()
    category_full = setting.category_full_name_map[category]
    freq_country_map = {
        "M": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("M", False)],
        "Q": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("Q", False)],
        "A": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("A", False)]
    }
    
    mapping_path = setting.category_structure[category_full]["path"]
    matcher = Export_matcher(mapping_path=mapping_path, keep_list=[1, 5, 3], category_name=category_full)
    
    freq_list = freq_country_map.keys() if freq_list is None else freq_list
    for freq in freq_list:
        country_list = freq_country_map[freq] if country_list is None \
            else [i for i in country_list if i in freq_country_map[freq]]
        for country in country_list:
            matcher.match(country=country, freq=freq)
        

def match_gdp(country_list, freq_list, category):
    setting = Setting()
    category_full = setting.category_full_name_map[category]
    setting = Setting()
    freq_country_map = {
        "M": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("M", False)],
        "Q": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("Q", False)],
        "A": [k for k, v in setting.structure.items() if category_full in v and v[category_full].get("A", False)]
    }
    
    mapping_path = setting.category_structure[category_full]["path"]
    matcher = GDP_matcher(mapping_path=mapping_path, keep_list=[0, 3, 4, 5, 6, 7, 1], category_name=category_full)

    freq_list = freq_country_map.keys() if freq_list is None else freq_list
    for freq in freq_list:
        country_list = freq_country_map[freq] if country_list is None \
            else [i for i in country_list if i in freq_country_map[freq]]
        for country in country_list:
            matcher.match(country=country, freq=freq)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--category')
    parser.add_argument('--country')
    parser.add_argument('--freq')
    args = parser.parse_args()
    
    funcs_map = {
        "gdp": match_gdp,
        'export': match_export
    }
    category_list = args.category.split(",") if args.category is not None else funcs_map.keys()
    country_list = args.country.split(",") if args.country is not None else None
    freq_list = args.freq.split(",") if args.freq is not None else None
    
    for category in category_list:
        funcs_map[category](country_list, freq_list)
    
    
if __name__ == "__main__":
    main()