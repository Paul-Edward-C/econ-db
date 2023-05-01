from lib.export_matcher import Export_matcher
from lib.gdp_matcher import GDP_matcher
from lib.tools import Setting
from datetime import datetime as dt


def match_export():
    setting = Setting()
    mapping_path = setting.category_structure["EXPORT"]["path"]
    matcher = Export_matcher(mapping_path=mapping_path, keep_list=[1, 5, 3])

    export_countries_m = [k for k, v in setting.structure.items() if "EXPORT" in v and v["EXPORT"].get("M", False)]
    print(f"EXPORT country : {export_countries_m}")
    
    for country in export_countries_m:
        matcher.match(data_path=setting.structure[country]["EXPORT"]["Monthly_data_path"],
                      output_path=f"db/{country.lower()}/data/export/{dt.strftime(dt.now().date(), '%Y%m%d')} {country} match output.xlsx",
                      country=country,
                      freq="M")
        

def match_gdp():
    setting = Setting()
    mapping_path = setting.category_structure["GDP"]["path"]
    matcher = GDP_matcher(mapping_path=mapping_path, keep_list=[0, 3, 4, 5, 6, 7, 1])
    
    gdp_countries_q = [k for k, v in setting.structure.items() if "GDP" in v and v["GDP"].get("Q", False)]
    print(f"GDP country : {gdp_countries_q}")

    # for country in gdp_countries_q:
    #     matcher.match(data_path=setting.structure[country]["GDP"]["Quarterly_data_path"],
    #                   output_path=f"db/{country.lower()}/data/gdp/{dt.strftime(dt.now().date(), '%Y%m%d')} {country} match output.xlsx",
    #                   country=country,
    #                   freq="Q")
    country = "JP"
    matcher.match(data_path=setting.structure[country]["GDP"]["Quarterly_data_path"],
                  output_path=f"db/{country.lower()}/data/gdp/{dt.strftime(dt.now().date(), '%Y%m%d')} {country} match output.xlsx",
                  country=country,
                  freq="Q")


def main():
    match_gdp()
    # match_export()
    
    
if __name__ == "__main__":
    main()