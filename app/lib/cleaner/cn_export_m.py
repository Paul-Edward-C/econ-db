import sys
import pathlib
import logging

import pandas as pd

sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent)}''')
sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent.parent)}''')
sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent.parent.parent)}''')

from lib.tools import Setting

setting = Setting()

data_path = setting.structure['CN']['Foreign Trade']["Monthly_data_path"]
data = pd.read_csv(data_path, index_col=[0])
mapping_template_path = setting.category_structure['Foreign Trade']['input_path']
mapping_template = pd.read_excel(mapping_template_path, index_col=None)

# Turn CNY into LCU
unit_list = [[g.strip() for g in i.split(',')] for i in mapping_template['Unit'].dropna().tolist()]
unit_component = list(set(item for sublist in unit_list for item in sublist))

columns = data.columns

# CNY bn into LCU
currency_replace_num = 0
currencies = ["CNY", "USD"]
currencies_dict = {
    "CNY": "LCU",
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
logging.info(f"Currency replace num : {currency_replace_num}")

# Change MoM chg into % MoM
# single_unit_dict = {
#     "MoM chg": "% MoM"
# }
# for unit in single_unit_dict.keys():
#     new_columns = []
#     for column in columns:
#         if unit in column:
#             column = column.replace(unit, single_unit_dict[unit])
#         new_columns.append(column)
#     columns = new_columns

# Check unit order
unit_replace_num = 0
new_columns = []
for column in columns:
    unit_num = 0
    for unit in unit_component:
        if unit in column:
            unit_num += 1
    
    right_unit_order = [", ".join(units).strip(", ") for units in unit_list if len(units) == unit_num]
    
    if len([i for i in right_unit_order if i in column]) == 0:
        print(column)
        cond_dict = {
            1: {
            
            },
            2: {
                "SA, % of total": "% of total, SA",
                "SA, LCU": "LCU, SA"
            },
            3: {
                "SA, LCU, % MoM": "% MoM, LCU, SA"
            }
        }
        # if any([i for i in cond_dict[unit_num].keys() if i in column]):
        #     print(column)
        
        new_columns.append(column)
    else:
        new_columns.append(column)
logging.info(f"Unit replace num : {unit_replace_num}")
data.columns = columns
data.to_csv(data_path, index=True)