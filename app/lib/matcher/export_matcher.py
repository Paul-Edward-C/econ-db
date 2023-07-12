# =========IMPORT PACKAGES==========
import logging
import pandas as pd
from fuzzywuzzy import fuzz
from datetime import datetime as dt
import numpy as np
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
import pathlib

sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent)}''')
sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent.parent)}''')
sys.path.append(f'''{str(pathlib.Path(__file__).resolve().parent.parent.parent)}''')
from lib.tools import Setting


# =========DEFINE CLASS OBJECT==========


class Export_matcher:
    def __init__(self, mapping_path, keep_list, category_name):
        # Define self.xxx in to every parameters in __init__
        for key, value in locals().items():
            if key != 'self':
                setattr(self, key, value)
            
        self.freq_lookup_table = {
            "M": ["Monthly"]
        }
        self.setting = Setting()
        
    def get_cosine_similarity(self, s1, s2):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([s1, s2])
        similarity = cosine_similarity(vectors[0], vectors[1])
    
        return similarity[0][0]
    
    def match(self, country, freq):
        all_result = pd.DataFrame()
        mapping = pd.read_csv(self.mapping_path, index_col=None)
        data_path = self.setting.structure[country][self.category_name][f"{self.setting.freq_structure_map[freq]}_data_path"]
        data = pd.read_csv(data_path, index_col=[0])

        for index in tqdm(mapping.index, desc=f'{country} processing mapping', unit='mapping'):
            mapping_list = mapping.iloc[[index]].T[index]
            
            if mapping_list[0] not in self.freq_lookup_table[freq]:
                continue
    
            if mapping_list[2] == "Value":
                mapping_list = mapping_list[[1, 5, 3]].dropna()
            else:
                mapping_list = mapping_list[[1, 5, 2, 3]].dropna()
    
            if "Total" in mapping_list:
                mapping_list.remove("Total")
    
            mapping_string = ", ".join(mapping_list)
    
            data_columns = data.columns
    
            for i in mapping_list:
                data_columns = data_columns[data_columns.str.lower().str.contains(i.lower())]
    
            data_columns_revised = data_columns.str.replace(", All", "")
    
            fuzzscore_list = []
            cosscore_list = []
            for i in data_columns_revised:
                fuzzscore = fuzz.token_sort_ratio(i, mapping_string) / 100
                cosscore = self.get_cosine_similarity(i, mapping_string)
        
                fuzzscore_list.append(fuzzscore)
                cosscore_list.append(cosscore)
    
            result = pd.DataFrame({"dataname": data_columns.tolist(), "fuzzscore": fuzzscore_list,
                                   "cosscore": cosscore_list}).sort_values(by=["cosscore", "fuzzscore"],
                                                                           ascending=False)
            result = result.loc[(result['fuzzscore'] > 0.6) & (result['cosscore'] > 0.5)]
    
            result['overallscore'] = (result['fuzzscore'] + result['cosscore']) / 2
            result['mappingname'] = mapping_string
            result['mappingindex'] = index
            result['matchinglength'] = len(result)
    
            result.index = range(len(all_result), len(all_result) + len(result))
    
            all_result = pd.concat([all_result, result], axis=0)

        duplicated_dataname_u = all_result[all_result['dataname'].duplicated()]['dataname'].unique()
        for duplicate in duplicated_dataname_u:
            duplicate_df = all_result.loc[all_result['dataname'] == duplicate].sort_values(by="overallscore",
                                                                                           ascending=False)
            all_result.drop(duplicate_df.index[1:], inplace=True)

        duplicated_mappingname_u = all_result[all_result['mappingname'].duplicated()]['mappingname'].unique()
        for duplicate in duplicated_mappingname_u:
            duplicate_df = all_result.loc[all_result['mappingname'] == duplicate].sort_values(by="overallscore",
                                                                                              ascending=False)
            all_result.drop(duplicate_df.index[1:], inplace=True)

        mapping.loc[all_result['mappingindex'], country] = all_result['dataname'].tolist()
        mapping.to_csv(self.mapping_path, index=False)
        output_path = f"db/{country.lower()}/export/{freq.lower()}/{dt.strftime(dt.now().date(), '%Y%m%d')} {country} match output.xlsx"
        all_result.to_excel(output_path, index=True)
        
        return all_result, mapping, len(all_result)
