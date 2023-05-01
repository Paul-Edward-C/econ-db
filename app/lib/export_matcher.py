# =========IMPORT PACKAGES==========
import pandas as pd
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime as dt
import numpy as np
from tqdm import tqdm
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
        
    def get_cosine_similarity(self, s1, s2):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([s1, s2])
        similarity = cosine_similarity(vectors[0], vectors[1])
    
        return similarity[0][0]
    
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
            
            if main_category == "Exports" and unit == "USD":
                print(mapping_list)
            
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
        
            if max_score < 60:
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

    def match2(self, data_path, output_path, country, freq):
        all_result = pd.DataFrame()
        mapping = pd.read_csv(self.mapping_path, index_col=None)
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
        all_result.to_excel(output_path, index=True)
        
        return all_result, mapping, len(all_result)
