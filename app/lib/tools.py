# ====================================================================================
# Author:David Ding
# Date:2023/02/17
# Purpose:
#
# ====================================================================================

import os
import warnings
from datetime import datetime as dt
from datetime import timedelta as td

# =========IMPORT PACKAGES==========
from typing import Any, Union

import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, Select
from bokeh.models.css import InlineStyleSheet
from dateutil import parser
from PIL import Image

warnings.filterwarnings(action="ignore")


# =========DEFINE CLASS==========
class Tool:
    def __init__(self):
        self.mapping_dict = None
        self.general_mapping = None
        self.matched_columns = None
        self.setting = Setting()
        self.source_backup = pd.DataFrame()
        self.data_setting_backup = pd.DataFrame()
        self.data_setting_backup.index.name = "name"

    def create_mapping_dict(self, df, keys, values, result=None, prefix=""):
        print("keys: ", keys)
        if result is None:
            result = {}

        if len(keys) == 1:
            for val in df[keys[0]].unique():
                result[str(prefix) + str(val)] = df[df[keys[0]] == val][values].unique().tolist()
        else:
            key = keys[0]
            for val in df[key].unique():
                new_prefix = str(prefix) + str(val)
                print("new_pref: ", new_prefix)
                sub_df = df[df[key] == val]
                result[new_prefix] = sub_df[keys[1]].unique().tolist()
                print("res: ", result[new_prefix])
                self.create_mapping_dict(df=sub_df, keys=keys[1:], values=values, result=result, prefix=new_prefix)

        self.mapping_dict = result
        return result

    def create_matched_columns_and_general_mapping(self, df, country, length):
        self.matched_columns = df[country].tolist()
        self.general_mapping = pd.concat([df[df.columns[:length]], df[[country]]], axis=1)

    def create_selects(self):

        structure = self.setting.structure
        category_structure = self.setting.category_structure
        country_select_options = list(structure.keys())
        country_select = Select(
            value=country_select_options[0],
            options=country_select_options,
            width=self.setting.select_width,
            title="Country",
            stylesheets=[self.setting.select_stylesheet],
        )

        category_select_options = list(structure[country_select.value].keys())
        category_select = Select(
            value=category_select_options[0],
            options=category_select_options,
            width=self.setting.select_width,
            title="Category",
            stylesheets=[self.setting.select_stylesheet],
        )

        mapping = pd.read_csv(category_structure[category_select.value]["path"])
        mapping = mapping[~mapping[country_select.value].isna()].replace(np.nan, "")
        print(mapping)
        mapping_dict = self.create_mapping_dict(
            df=mapping,
            keys=mapping.columns[: category_structure[category_select.value]["length"] - 1],
            values=mapping.columns[category_structure[category_select.value]["length"] - 1],
        )
        self.create_matched_columns_and_general_mapping(
            df=mapping, country=country_select.value, length=category_structure[category_select.value]["length"]
        )

        first_term_options = sorted(mapping[mapping.columns[0]].unique().tolist())
        freq_select_options = []
        for option in first_term_options:
            if option[-1] not in freq_select_options:
                freq_select_options.append(option[-1])

        freq_select = Select(
            value=freq_select_options[0],
            options=freq_select_options,
            width=self.setting.select_width,
            title="Frequency",
            stylesheets=[self.setting.select_stylesheet],
        )

        sector_select_options = []
        for option in first_term_options:
            if option[0] == 'N':
                if 'Nominal' not in sector_select_options:
                    sector_select_options.append("Nominal")
            if option[0] == 'R':
                if 'Real' not in sector_select_options:
                    sector_select_options.append("Real")
            if option[0] == 'D':
                if 'Deflator' not in sector_select_options:
                    sector_select_options.append("Deflator")
        sector_select = Select(
            value=sector_select_options[0],
            options=sector_select_options,
            width=self.setting.select_width,
            title="Sector",
            stylesheets=[self.setting.select_stylesheet],
        )

        freq_sect_str = ''
        if sector_select.value == 'Deflator':
            freq_sect_str += 'Deflator '
        elif sector_select.value == 'Nominal':
            freq_sect_str += 'NGDP '
        elif sector_select.value == 'Real':
            freq_sect_str += 'RGDP '
        freq_sect_str += freq_select.value

        # unit_select_options = sorted(mapping_dict[freq_select.value])\
        unit_select_options = sorted(mapping_dict[freq_sect_str])
        unit_select = Select(
            value="LCU",
            options=unit_select_options,
            width=self.setting.select_width,
            title="Unit",
            stylesheets=[self.setting.select_stylesheet],
        )

        # type_select_options = sorted(mapping_dict[freq_select.value + unit_select.value])
        type_select_options = sorted(mapping_dict[freq_sect_str + unit_select.value])
        type_select = Select(
            value="Expenditure",
            options=type_select_options,
            width=self.setting.select_width,
            title="Type",
            stylesheets=[self.setting.select_stylesheet],
        )

        # cat1_select_options = sorted(mapping_dict[freq_select.value + unit_select.value + type_select.value])
        cat1_select_options = sorted(mapping_dict[freq_sect_str + unit_select.value + type_select.value])
        cat1_select = Select(
            value=cat1_select_options[0],
            options=cat1_select_options,
            width=self.setting.select_width,
            title="Data category 1",
            stylesheets=[self.setting.select_stylesheet],
        )



        # cat2_select_options = sorted(
        #     mapping_dict[freq_select.value + unit_select.value + type_select.value + cat1_select.value]
        # )
        cat2_select_options = sorted(
            mapping_dict[freq_sect_str + unit_select.value + type_select.value + cat1_select.value]
        )
        cat2_select = Select(
            value=cat2_select_options[0],
            options=cat2_select_options,
            width=self.setting.select_width,
            title="Data category 2",
            stylesheets=[self.setting.select_stylesheet],
        )

        #cat3_select_options = sorted(
        #    mapping_dict[
        #        freq_select.value + unit_select.value + type_select.value + cat1_select.value + cat2_select.value
        #    ]
        #)
        cat3_select_options = sorted(
            mapping_dict[
                freq_sect_str + unit_select.value + type_select.value + cat1_select.value + cat2_select.value
            ]
        )
        cat3_select = Select(
            value=cat3_select_options[0],
            options=cat3_select_options,
            width=self.setting.select_width,
            title="Data category 3",
            stylesheets=[self.setting.select_stylesheet],
        )

        cat4_select_options = sorted(
            mapping_dict[
                # freq_select.value
                freq_sect_str
                + unit_select.value
                + type_select.value
                + cat1_select.value
                + cat2_select.value
                + cat3_select.value
            ]
        )
        cat4_select = Select(
            value=cat4_select_options[0],
            options=cat4_select_options,
            width=self.setting.select_width,
            title="Data category 4",
            stylesheets=[self.setting.select_stylesheet],
        )
        cat5_select_options = sorted(
            mapping_dict[
                # freq_select.value
                freq_sect_str
                + unit_select.value
                + type_select.value
                + cat1_select.value
                + cat2_select.value
                + cat3_select.value
                + cat4_select.value
            ]
        )
        cat5_select = Select(
            value=cat5_select_options[0],
            options=cat4_select_options,
            width=self.setting.select_width,
            title="Data category 5",
            stylesheets=[self.setting.select_stylesheet],
        )
        
        return (
            country_select,
            category_select,
            freq_select,
            sector_select,
            unit_select,
            type_select,
            cat1_select,
            cat2_select,
            cat3_select,
            cat4_select,
            cat5_select,
        )

    def get_column_by_selects(
        self,
        country_select,
        freq_select,
        sector_select,
        unit_select,
        type_select,
        cat1_select,
        cat2_select,
        cat3_select,
        cat4_select,
        cat5_select,
        category_len,
    ):
        
        freq_sect_str = ''
        if sector_select.value == 'Deflator':
            freq_sect_str += 'Deflator '
        elif sector_select.value == 'Nominal':
            freq_sect_str += 'NGDP '
        elif sector_select.value == 'Real':
            freq_sect_str += 'RGDP '
        freq_sect_str += freq_select.value
        
        if freq_sect_str == "M":
            select_value_list = [
                i.value
                for i in [
                    sector_select,
                    type_select,
                    unit_select,
                    cat1_select,
                    cat2_select,
                    cat3_select,
                    cat4_select,
                    cat5_select,
                ]
            ]
            select_value_list.insert(0, "Monthly")
            select_value_list.pop
        else:
            select_value_list = [
                i.value
                for i in [
                    unit_select,
                    type_select,
                    cat1_select,
                    cat2_select,
                    cat3_select,
                    cat4_select,
                    cat5_select,
                ]
            ]
            select_value_list.insert(0, freq_sect_str)
        
        dummy = (
            self.general_mapping.loc[:, [str(i) for i in range(category_len)]] == select_value_list[:category_len]
        ).all(axis=1)
        col_name = self.general_mapping.loc[dummy, country_select.value].values[0]

        return col_name

    def read_data(self, setting_path, data_path, matched_columns=None):  # Still need to unify the date when reading
        self.data_setting = pd.read_csv(setting_path, index_col=[0])

        data = pd.read_csv(data_path, index_col=[0]).dropna(how="all", axis=0)
        data.index = pd.to_datetime(data.index)
        data = data.resample("M").last()

        data_cols = data.columns.values.tolist()
        self.data = data[matched_columns] if matched_columns is not None and matched_columns in data_cols else data
        self.data.index = pd.to_datetime(self.data.index)
        return self.data, self.data_setting

    def create_data_setting_object(self, data_setting, col_name):
        data_setting_backup_cols = ["display_name", "data_type", "chart_type"]
        data_col_name = "_".join(col_name.split("_")[:-1])
        try:
            self.data_setting_backup.loc[col_name, data_setting_backup_cols] = data_setting.loc[data_col_name].tolist()
        except Exception as e:
            pass
        data_setting_object = self.data_setting_backup.loc[[col_name]].reset_index().loc[0].to_dict()

        return data_setting_object

    def add_source_column(self, source, col_name, index_date_input_value):  # new refer to a new data in source_backup

        source_df = pd.DataFrame(source.data)

        sub_name = "_".join(col_name.split("_")[:-1])

        if self.source_backup.empty:
            new_source_df = self.data[[sub_name]]
            new_source_df.columns = [col_name]
            self.source_backup = new_source_df

        else:
            source_df = source_df.set_index("Date")
            try:
                new_source_df = pd.concat([source_df, self.source_backup[[col_name]]], axis=1)
            except Exception as e:
                new_col_df = self.data[[sub_name]]
                new_col_df.columns = [col_name]
                new_source_df = pd.concat([source_df, new_col_df], axis=1)
                self.source_backup = pd.concat([self.source_backup, new_col_df], axis=1)

        # remove all "_index" columns from self.source_backup
        valid_columns = [i for i in self.source_backup.columns if "_index" not in i]
        self.source_backup = self.source_backup[valid_columns]

        # Deal with index data part (all index data need to use new ref_date to be starting point)
        index_ref_date = self.get_index_input_date(index_date_input_value)
        self.source_backup_index = (self.source_backup / self.source_backup.loc[index_ref_date]) * 100
        for i in new_source_df.columns:
            if "_index" not in i:
                new_source_df[f"{i}_index"] = self.source_backup_index[i]

        new_source_df.dropna(how="all", axis=0, inplace=True)
        source = ColumnDataSource(new_source_df)

        return source, index_ref_date

    def update_index_source(self, source, index_date_input_value):
        source_df = pd.DataFrame(source.data).set_index("Date")
        used_columns = [i for i in source_df.columns if "_index" not in i]

        index_ref_date = self.get_index_input_date(index_date_input_value)

        source_df.dropna(how="all", axis=0, inplace=True)
        self.source_backup_index = (self.source_backup / self.source_backup.loc[index_ref_date]) * 100
        for i in used_columns:
            source_df[f"{i}_index"] = self.source_backup_index[i]

        source_df.dropna(how="all", axis=0, inplace=True)
        source = ColumnDataSource(source_df)

        return source, index_ref_date

    def get_source_limitvalues(self, data):
        maximum = data.iloc[:, 1:].max().max()
        minimum = data.iloc[:, 1:].min().min()

        if maximum > 0:
            maximum *= self.setting.axis_ratio
        else:
            maximum /= self.setting.axis_ratio

        if minimum < 0:
            minimum *= self.setting.axis_ratio
        else:
            minimum /= self.setting.axis_ratio

        return minimum, maximum

    def create_rgba_from_file(self, path):
        lena_img = Image.open(path).convert("RGBA")
        xdim, ydim = lena_img.size

        img = np.empty((ydim, xdim), dtype=np.uint32)
        view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
        view[:, :, :] = np.flipud(np.asarray(lena_img))

        dim = max(xdim, ydim)
        return img, xdim, ydim, dim

    def get_index_input_date(self, starting_date):
        starting_date = str(starting_date).strip()

        try:
            starting_date = parser.parse(starting_date)
        except Exception as e:
            starting_date = self.setting.index_default_date

        nearest_date = sorted([(i, abs(i - starting_date)) for i in self.source_backup.index], key=lambda x: x[1])[0][0]

        return dt.strftime(nearest_date, "%Y/%m/%d")

    def remove_duplicated_unit(self, unit_list):
        result = []
        for i, string in enumerate(unit_list):
            is_contained = False
            for j, other_string in enumerate(unit_list):
                if i != j and string in other_string:
                    is_contained = True
                    break
            if not is_contained:
                result.append(string)
        return result


class Setting:
    def __init__(self):
        self.create_styles()
        self.theme_file_path = "lib/theme/theme.yml"
        self.curdoc_name = "ECON DB"

        self.line_width = 2
        self.bar_width = td(days=60)
        self.figure_width = 1000
        self.figure_height = 500
        self.range_height = 100
        self.select_width = 500
        self.button_width = 100
        self.datatable_column_width = 500

        self.axis_ratio = 1.2

        self.multichoice_width = int(self.figure_width + self.datatable_column_width - 3 * self.button_width)

        self.background_image_path = "static/background_image_300.png"

        # color setting
        self.bar_border_color = "#000000"
        self.colors = [
            {"id": 0, "color": "#191970", "used": False, "label": "midnightblue"},
            {"id": 1, "color": "#006400", "used": False, "label": "darkgreen"},
            {"id": 2, "color": "#8b0000", "used": False, "label": "darkred"},
            {"id": 3, "color": "#4b0082", "used": False, "label": "indigo"},
            {"id": 4, "color": "#ff8c00", "used": False, "label": "darkorange"},
            {"id": 5, "color": "#000000", "used": False, "label": "black"},
            {"id": 6, "color": "#dc143c", "used": False, "label": "crimson"},
            {"id": 7, "color": "#87cefa", "used": False, "label": "lightskyblue"},
        ]

        self.freq_data_mapping_map = {"Q": {"NGDP Q": "NGDP", "RGDP Q": "RGDP", "Deflator Q" : "Deflator"}, "M": {"Monthly": "Monthly"}}

        self.country_currency_map = {
            "KR": {"KRW": "LCU", "USD": "USD"},
            "TW": {"TWD": "LCU", "NTD": "LCU", "USD": "USD"},
            "JP": {"JPY": "LCU", "USD": "USD"},
            "CN": {"CNY": "LCU", "USD": "USD"},
        }
        self.category_full_name_map = {
            "export": "Foreign Trade",
            "gdp": "National Accounts",
            "inflation": "Inflation"
        }

        self.freq_full_name_map = {"Q": "Quarterly", "M": "Monthly", "A": "Annual"}

        # first three selects setting
        self.structure = {
            "JP": {
                "National Accounts": {
                    "Q": True,
                    "Quarterly_data_path": "db/jp/gdp/q/jp_gdp_q.csv",
                    "Quarterly_raw_data_path": "db/jp/gdp/q/jp_gdp_q_raw.csv",
                    "Quarterly_setting_path": "db/jp/gdp/q/jp_gdp_q_setting.csv",
                    "Quarterly_temp_setting_path": "db/jp/gdp/q/jp_gdp_q_setting_temp.csv",
                },
                "Foreign Trade": {
                    "M": True,
                    "Monthly_data_path": "db/jp/export/m/jp_export_m.csv",
                    "Monthly_raw_data_path": "db/jp/export/m/jp_export_m_raw.csv",
                    "Monthly_setting_path": "db/jp/export/m/jp_export_m_setting.csv",
                    "Monthly_temp_setting_path": "db/jp/export/m/jp_export_m_setting_temp.csv",
                },
            },
            "TW": {
                "National Accounts": {
                    "Q": True,
                    "Quarterly_data_path": "db/tw/gdp/q/tw_gdp_q.csv",
                    "Quarterly_raw_data_path": "db/tw/gdp/q/tw_gdp_q_raw.csv",
                    "Quarterly_setting_path": "db/tw/gdp/q/tw_gdp_q_setting.csv",
                    "Quarterly_temp_setting_path": "db/tw/gdp/q/tw_gdp_q_setting_temp.csv",
                },
                "Foreign Trade": {
                    "M": True,
                    "Monthly_data_path": "db/tw/export/m/tw_export_m.csv",
                    "Monthly_raw_data_path": "db/tw/export/m/tw_export_m_raw.csv",
                    "Monthly_setting_path": "db/tw/export//m/tw_export_m_setting.csv",
                    "Monthly_temp_setting_path": "db/tw/export//m/tw_export_m_setting_temp.csv",
                },
            },
            "KR": {
                "National Accounts": {
                    "Q": True,
                    "Quarterly_data_path": "db/kr/gdp/q/kr_gdp_q.csv",
                    "Quarterly_raw_data_path": "db/kr/gdp/q/kr_gdp_q_raw.csv",
                    "Quarterly_setting_path": "db/kr/gdp/q/kr_gdp_q_setting.csv",
                    "Quarterly_temp_setting_path": "db/kr/gdp/q/kr_gdp_q_setting_temp.csv",
                },
                "Foreign Trade": {
                    "M": True,
                    "Monthly_data_path": "db/kr/export/m/kr_export_m.csv",
                    "Monthly_raw_data_path": "db/kr/export/m/kr_export_m_raw.csv",
                    "Monthly_setting_path": "db/kr/export/m/kr_export_m_setting.csv",
                    "Monthly_temp_setting_path": "db/kr/export/m/kr_export_m_setting_temp.csv",
                },
            },
            "CN": {
                "National Accounts": {
                    "Q": True,
                    "Quarterly_data_path": "db/cn/gdp/q/cn_gdp_q.csv",
                    "Quarterly_raw_data_path": "db/cn/gdp/q/cn_gdp_q_raw.csv",
                    "Quarterly_setting_path": "db/cn/gdp/q/cn_gdp_q_setting.csv",
                    "Quarterly_temp_setting_path": "db/cn/gdp/q/cn_gdp_q_setting_temp.csv",
                },
                "Foreign Trade": {
                    "M": True,
                    "Monthly_data_path": "db/cn/export/m/cn_export_m.csv",
                    "Monthly_raw_data_path": "db/cn/export/m/cn_export_m_raw.csv",
                    "Monthly_setting_path": "db/cn/export/m/cn_export_m_setting.csv",
                    "Monthly_temp_setting_path": "db/cn/export/m/cn_export_m_setting_temp.csv",
                },
            },
        }

        self.category_structure = {
            "National Accounts": {
                "input_path": "db/mapping/gdp/gdp_mapping_template.xlsx",
                "path": "db/mapping/gdp/gdp_mapping.csv",
                "length": 8,
                "display_name": "",
            },
            "Foreign Trade": {
                "input_path": "db/mapping/export/export_mapping_template.xlsx",
                "path": "db/mapping/export/export_mapping.csv",
                "length": 7,
                "display_name": "",
            },
        }

        self.download_button_path = "lib/js_code/download_button_callback.js"

        self.index_default_date = dt(2019, 3, 31)

    def create_styles(self):

        button_style_path = "lib/style/button_styles.css"
        self.button_stylesheet = InlineStyleSheet(css=open(button_style_path).read())

        select_style_path = "lib/style/select_styles.css"
        self.select_stylesheet = InlineStyleSheet(css=open(select_style_path).read())

        datatable_style_path = "lib/style/datatable_styles.css"
        self.datatable_stylesheet = InlineStyleSheet(css=open(datatable_style_path).read())
