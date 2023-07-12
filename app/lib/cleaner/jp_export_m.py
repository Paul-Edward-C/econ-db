import sys
import pathlib
import logging
import argparse

import pandas as pd

sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent)}''')
sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent.parent)}''')
sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent.parent.parent)}''')

from lib.tools import Setting


def main(to_db=False):
    setting = Setting()
    
    data_path = setting.structure['JP']['Foreign Trade']["Monthly_data_path"]
    data = pd.read_csv(data_path, index_col=[0])
    mapping_template_path = setting.category_structure['Foreign Trade']['input_path']
    mapping_template = pd.read_excel(mapping_template_path, index_col=None)
    
    # Turn JPY into LCU
    unit_list = [[g.strip() for g in i.split(',')] for i in mapping_template['Unit'].dropna().tolist()]
    unit_component = list(set(item for sublist in unit_list for item in sublist))
    
    columns = data.columns
    
    # CNY bn into LCU
    currency_replace_num = 0
    currencies_dict = {
        "JPY": "LCU",
        "USD": "USD"
    }
    for currency in currencies_dict.keys():
        new_columns = []
        for column in columns:
            if currency in column:
                column = column.replace(f"{currency} bn", currencies_dict[currency])
                currency_replace_num += 1
            new_columns.append(column)
        columns = new_columns
    
    
    # Check unit order
    print(unit_component)
    unit_replace_num = 0
    new_columns = []
    for column in columns:
        unit_num = 0
        for unit in unit_component:
            if unit in column:
                unit_num += 1
        
        right_unit_order = [", ".join(units).strip(", ") for units in unit_list if len(units) == unit_num]
        
        if len([i for i in right_unit_order if i in column]) == 0:
            cond_dict = {
                0: {
                
                },
                1: {
                
                },
                2: {
                    # "SA, % of total": "% of total, SA",
                    "SA, LCU": "LCU, SA",
                    "SA, USD": "USD, SA",
                    "SA, % MoM": "% MoM, SA",
                    "SA, % YoY": "% YoY, SA"
                },
                3: {
                    "SA, LCU, % MoM": "LCU, % MoM, SA",
                    "SA, USD, % MoM": "USD, % MoM, SA",
                    "SA, LCU, % YoY": "LCU, % YoY, SA",
                    "SA, USD, % YoY": "USD, % YoY, SA",
                    "SA, index, % YoY": "index, % YoY, SA"
                }
            }
            
            check_list = [i for i in cond_dict[unit_num].keys() if i in column]  # Ideally this list length will be one.
            if len(check_list) == 1:
                column = column.replace(check_list[0], cond_dict[unit_num][check_list[0]])
                unit_replace_num += 1
            else:
                print(column, unit_num, len(check_list))
            
            new_columns.append(column)
        else:
            new_columns.append(column)
    print(f"Currency replace num : {currency_replace_num}")
    print(f"Unit replace num : {unit_replace_num}")
    data.columns = columns
    
    if to_db:
        data.to_csv(data_path, index=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--to_db", action="store_true")
    args = parser.parse_args()
    
    if args.to_db:
        main(to_db=True)
    
    else:
        main()

