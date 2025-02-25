import pickle as pkl
import pandas as pd
import os

def main():
    df = pd.read_csv("db\jp\export\m\jp_export_m_raw.csv")
    cat_dict = {}

    for column in df.columns:

        if column == "Date":
            continue
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
            curr_index += 1


    file_path = "jp_export_test.pkl"

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"File '{file_path}' not found.")

    with open('jp_export_test.pkl', 'wb') as f:
        pkl.dump(cat_dict, f)


if __name__ == "__main__":
    main()