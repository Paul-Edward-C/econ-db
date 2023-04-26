# =========IMPORT PACKAGES==========
import itertools
import pandas as pd


# =========DEFINE CLASS OBJECT==========


class Mapping_generator:
    def __init__(self, input_path, output_path, sep="Subcategories"):
        for key, value in locals().items():
            if key != 'self':
                setattr(self, key, value)
    
        self.mapping = self.create_mapping()
        
       
    def create_mapping(self):
        template = pd.read_excel(self.input_path, index_col=None)
    
        iter_columns = template.columns[:list(template.columns).index(self.sep)]
        iter_df = template[iter_columns].dropna(how='all')
    
        tier_df = template[template.columns[list(template.columns).index(self.sep):]].set_index(self.sep).dropna(how='any')
        length = len(iter_df.columns)
    
        self.iter_result = self.create_iterdf(iter_df)
        self.tier_result = self.create_tierdf(tier_df, length)
    
        result = self.merge_dataframes(self.iter_result, self.tier_result)
        result.to_csv(self.output_path, index=False)
    
        return result
    
    def create_iterdf(self, df):
        combinations = list(itertools.product(*df.values.T))
    
        df_new = pd.DataFrame(combinations).dropna(how='any')
        return df_new

    def create_tierdf(self, source, length):
        temp = pd.DataFrame()
        col_dict = {}
    
        for index in range(len(source.index)):
            if index == len(source) - 1:
                break
        
            current_order = int(source.iloc[index]["Tier"])
            next_order = int(source.iloc[index + 1]["Tier"])
        
            col_dict[current_order] = source.index[index].strip()
        
            if current_order >= next_order:
                temp.loc[len(temp), [i for i in range(length, current_order + 1)]] = [col_dict[i] for i in
                                                                                      range(length, current_order + 1)]
        return temp

    def merge_dataframes(self, df1, df2):
        cols1 = df1.columns
        cols2 = df2.columns
    
        values1 = df1.values
        values2 = df2.values
    
        combinations = list(itertools.product(values1, values2))
        
        merged_cols = list(cols1) + list(cols2)
        merged_rows = []
        for combo in combinations:
            merged_rows.append(list(combo[0]) + list(combo[1]))
    
        merged_df = pd.DataFrame(merged_rows, columns=merged_cols)
    
        return merged_df


