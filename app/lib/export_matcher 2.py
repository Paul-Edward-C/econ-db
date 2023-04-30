# =========IMPORT PACKAGES==========
import pandas as pd
from fuzzywuzzy import fuzz
from datetime import datetime as dt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========DEFINE CLASS OBJECT==========


class Export_matcher:
    def __init__(self, mapping_path, keep_list, category="EXPORT"):
        # Define self.xxx in to every parameters in __init__
        for key, value in locals().items():
            if key != 'self':
                setattr(self, key, value)
            
        self.freq_lookup_table = {
            "M": ["Monthly"]
        }

    def match(self, data_path, output_path, country, freq):
        result_list = []

        # data_path = f"db/{country.lower()}/data/{category.lower()}/{country.lower()}_{category.lower()}_m.csv"
        # mapping_path = f"db/mapping/{category.lower()}/{category.lower()}_mapping.csv"
        # data_export_path = f"db/{country.lower()}/data/{category.lower()}/{dt.strftime(dt.today().date(), '%Y%m%d')} {country} matching output.xlsx"
    
        mapping = pd.read_csv(self.mapping_path, index_col=None)
        data = pd.read_csv(data_path, index_col=[0])
        for index in mapping.index:
            if mapping.loc[index][0] not in self.freq_lookup_table[freq]:
                continue
            
            # print(self.keep_list)
            mapping_list = mapping.iloc[[index]].T.iloc[self.keep_list].dropna()[index].to_list()
            # print(mapping_list)
            
            if len(mapping_list) == 0:
                print(country, index)
        
            mapping_list.remove("Total") if "Total" in mapping_list else None
        
            unit = mapping_list[-1]
            main_category = mapping_list[0]
            result = ", ".join(mapping_list)
        
            data_columns = data.columns
            
            # exclude data without main category and unit in its name
            for i in [main_category, unit]:
                data_columns = data_columns[data_columns.str.contains(i)]
        
            if len(data_columns) == 0:
                result_list.append(
                    {"mapping name": result, "data name": np.nan, "score": 0, "length": len(data_columns)})
                continue
        
            max_score = 0
            data_name = ""
        
            for i in data_columns:
                score = fuzz.token_sort_ratio(result, i)
                if score > max_score:
                    max_score = score
                    data_name = i
        
            if max_score < 75:
                result_list.append(
                    {"mapping name": result, "data name": np.nan, "score": 0, "length": len(data_columns),
                     "mapping_index": index})
                continue
        
            result_list.append(
                {"mapping name": result, "data name": data_name, "score": max_score / 100, "length": len(data_columns),
                 "mapping_index": index})
    
        result = pd.DataFrame(result_list)
    
        # remove multiple mapping to same data issue
        data_found = result['data name'].dropna().unique()
        for i in range(len(data_found)):
            filter_data = result[result['data name'] == data_found[i]]
            if len(filter_data) > 1:
                for g in filter_data.sort_values("score", ascending=False).index[1:]:
                    result.loc[g, ["data name", "score", "length"]] = [np.nan, 0, 0]
                
                    # Output result
        result.to_excel(output_path, index=False)
        result_length = len(result.dropna(how='any', axis=0))
    
        # Write the matched data to mapping
        for index, row in result.iterrows():
            mapping.loc[row['mapping_index'], country] = row['data name']
    
        mapping.dropna(how="all", axis=0, inplace=True)
        mapping.to_csv(self.mapping_path, index=False)
    
        return result, mapping, result_length

