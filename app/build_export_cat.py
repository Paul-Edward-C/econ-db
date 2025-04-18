import pickle as pkl
import sys
import pandas as pd
import os

def build(raw_data_path, pkl_path):
    df = pd.read_csv(raw_data_path)
    cat_dict = {}
    complete_keys = []

    for column in df.columns:
        if column == "Date":
            continue
        column_temp = column
        cat_lst = column.split(", ")

        key = ""
        curr_index = 1

        for cat in cat_lst[0:-1]:
            key += cat
            key += ", "
            new_field = cat_lst[curr_index]
            
            if key in cat_dict:
                curr_options = cat_dict[key]
                if new_field not in curr_options:
                    curr_options.append(new_field)
            else:
                cat_dict[key] = [new_field]
                if key[0:-2] in complete_keys:
                    print("jello")
                    cat_dict[key].append("No Option")
            curr_index += 1

        complete_keys.append(column_temp)
        



    if os.path.exists(pkl_path):
        os.remove(pkl_path)
        print(f"File '{pkl_path}' deleted successfully.")

    with open(pkl_path, 'wb') as f:
        pkl.dump(cat_dict, f)
