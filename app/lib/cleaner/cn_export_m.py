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
for currency in currencies:
    new_columns = []
    for column in columns:
        if currency in column:
            new_columns.append(column.replace(f"{currency} bn", "LCU"))
            currency_replace_num += 1
        else:
            new_columns.append(column)
    columns = new_columns
logging.info(f"Currency replace num : {currency_replace_num}")

# Check unit order
unit_replace_num = 0
new_columns = []
for column in columns:
    unit_num = 0
    for unit in unit_component:
        if unit in column:
            unit_num += 1
    
    right_unit_order = [", ".join(units).strip(", ") for units in unit_list if len(units) == unit_num]
    if not any([i for i in right_unit_order if i in column]):
        cond1 = "SA, LCU"
        cond2 = "SA, % of total"
        
        if cond1 in column:
            column = column.replace(cond1, "LCU, SA")
            unit_replace_num += 1
        
        elif cond2 in column:
            column = column.replace(cond2, "% of total, SA")
            unit_replace_num += 1
        
        else:
            print(column)
        new_columns.append(column)
    else:
        new_columns.append(column)
logging.info(f"Unit replace num : {unit_replace_num}")
data.columns = columns
data.to_csv(data_path, index=True)