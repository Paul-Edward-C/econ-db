# ====================================================================================
# Author:David Ding
# Date:2023/02/17
# Purpose:
#
# ====================================================================================

# ====================================================================================
# Debug Imports
import ctypes
from bokeh.models import TabPanel, Tabs, Button, Paragraph
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
# ====================================================================================

import os
import time
from datetime import datetime as dt
from datetime import timedelta as td
from math import floor

import logging
import numpy as np
import pandas as pd
from bokeh.core.properties import value
from bokeh.io import curdoc
from bokeh.layouts import column, row

# =========IMPORT PACKAGES==========
from bokeh.models import (
    BoxZoomTool,
    Button,
    ColumnDataSource,
    DataTable,
    DateFormatter,
    HoverTool,
    MultiChoice,
    NumberFormatter,
    NumeralTickFormatter,
    PanTool,
    Range1d,
    RangeTool,
    ResetTool,
    TableColumn,
    TablerIcon,
    TextInput,
    Toggle,
    WheelZoomTool,
)
from bokeh.plotting import figure
from bokeh.themes import Theme
from lib.tools import Setting, Tool

# TablerIcon : https://tabler-icons.io/


# Specify working directory
dir_path = os.path.dirname(os.path.abspath(__file__))
# Change the working directory to the script directory
os.chdir(dir_path)
print(os.getcwd())

# =========GLOBAL VARIABLES=========

setting = Setting()
tool = Tool()
x_range_start_index = -30
x_range_end_index = -1
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
first_add = True      # remove once index button is fixed


# =========DEFINE FUNCTION=========


def update_selects_format():
    selects_list = [
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
    ]
    new_len = next((i for i, select in enumerate(selects_list) if select.value == ""), len(selects_list))
    print(new_len)
    if new_len == 6:
        new_layout = row(
            column(country_select, category_select, freq_select, sector_select),
            column(unit_select, type_select),
            column(),
        )

    if new_len == 7:
        new_layout = row(
            column(country_select, category_select, freq_select, sector_select),
            column(unit_select, type_select, cat1_select),
            column(),
        )
    elif new_len == 8:
        new_layout = row(
            column(country_select, category_select, freq_select, sector_select),
            column(unit_select, type_select, cat1_select),
            column(cat2_select),
        )
    elif new_len == 9:
        new_layout = row(
            column(country_select, category_select, freq_select, sector_select),
            column(unit_select, type_select, cat1_select),
            column(cat2_select, cat3_select),
        )
    elif new_len == 10:
        new_layout = row(
            column(country_select, category_select, freq_select, sector_select),
            column(unit_select, type_select, cat1_select),
            column(cat2_select, cat3_select, cat4_select),
        )
    elif new_len == 11:
        new_layout = row(
            column(country_select, category_select, freq_select, sector_select),
            column(unit_select, type_select, cat1_select, cat2_select),
            column(cat3_select, cat4_select, cat5_select),
        )
    layout.children[0] = new_layout

def make_freq_sect_str(freq_val, sect_val):
    if freq_select.value == "M":
        return "Monthly"
    freq_sect_str = ''
    if sector_select.value == 'Deflator':
        freq_sect_str += 'Deflator '
    elif sector_select.value == 'Nominal':
        freq_sect_str += 'NGDP '
    elif sector_select.value == 'Real':
        freq_sect_str += 'RGDP '
    freq_sect_str += freq_select.value
    return freq_sect_str

def update_country_select(attrname, old, new):
    category_select_options = list(setting.structure[country_select.value].keys())
    category_select.options = category_select_options
    if category_select.value not in category_select_options:
        category_select.value = category_select_options[0]


def update_category_select(attrname, old, new):
    # Change to new columns
    os.chdir(dir_path)
    mapping_raw = pd.read_csv(setting.category_structure[category_select.value]["path"])
    mapping_raw = mapping_raw[~mapping_raw[country_select.value].isna()].replace(np.nan, "")

    category_len = setting.category_structure[category_select.value]["length"]

    global mapping_dict
    mapping_dict = tool.create_mapping_dict(
        df=mapping_raw, keys=mapping_raw.columns[: category_len - 1], values=mapping_raw.columns[category_len - 1]
    )

    # Create new general mapping and matched columns
    tool.create_matched_columns_and_general_mapping(
        df=mapping_raw, country=country_select.value, length=setting.category_structure[category_select.value]["length"]
    )

    global mapping
    mapping = tool.general_mapping

    global matched_columns
    matched_columns = tool.matched_columns

    # Create options for next select
    first_term_options = sorted(mapping[mapping.columns[0]].unique().tolist())
    freq_select_options = []
    for option in first_term_options:
        if option == "Monthly":
            if "M" not in freq_select_options:
                freq_select_options.append(option[0])
        else:
            if option[-1] not in freq_select_options:
                freq_select_options.append(option[-1])


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
    freq_select.options = freq_select_options
    sector_select.options = sector_select_options
    if freq_select.value not in freq_select_options:
        freq_select.value = freq_select_options[0]
    

def update_freq_select(attrname, old, new):
    # Change data source and data setting
    global data, data_setting

    freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)

    for i in setting.freq_data_mapping_map.keys():
        if freq_sect_str in setting.freq_data_mapping_map[i]:
            data, data_setting = tool.read_data(
                data_path=setting.structure[country_select.value][category_select.value][
                    f"{setting.freq_full_name_map[i]}_data_path"
                ],
                setting_path=setting.structure[country_select.value][category_select.value][
                    f"{setting.freq_full_name_map[i]}_setting_path"
                ],
                matched_columns=matched_columns,
            )
            break

    
    if category_select.value == "Foreign Trade":
        sector_select_options = mapping_dict["Monthly"]
        sector_select.options = sector_select_options
        if sector_select.value not in sector_select_options:
            sector_select.value = sector_select_options[0]
    else:
        sector_select_options = []
        first_term_options = sorted(mapping[mapping.columns[0]].unique().tolist())
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
        if sector_select.value not in sector_select_options:
            sector_select.value = sector_select_options[0]
        
        freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
        
        unit_select_options = mapping_dict[freq_sect_str]
        unit_select.options = unit_select_options
        if unit_select.value not in unit_select_options:
            unit_select.value = unit_select_options[0]

def update_sector_select(attrname, old, new):
    # Change data source and data setting
    if category_select.value == "National Accounts":
        global data, data_setting
        freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)

        for i in setting.freq_data_mapping_map.keys():
            if freq_sect_str in setting.freq_data_mapping_map[i]:
                data, data_setting = tool.read_data(
                    data_path=setting.structure[country_select.value][category_select.value][
                        f"{setting.freq_full_name_map[i]}_data_path"
                    ],
                    setting_path=setting.structure[country_select.value][category_select.value][
                        f"{setting.freq_full_name_map[i]}_setting_path"
                    ],
                    matched_columns=matched_columns,
                )
                break

        unit_select_options = mapping_dict[freq_sect_str]
        unit_select.options = unit_select_options

        if unit_select.value not in unit_select_options:
            unit_select.value = unit_select_options[0]
    
    elif category_select.value == "Foreign Trade":
        type_select_options = mapping_dict["Monthly" + sector_select.value]
        type_select.options = type_select_options

        if type_select.value not in type_select_options:
            type_select.value = type_select_options[0]


def update_unit_select(attrname, old, new):
    if category_select.value == "National Accounts":
        freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
        type_select_options = mapping_dict[freq_sect_str + unit_select.value]
        type_select.options = type_select_options

        if type_select.value not in type_select_options:
            type_select.value = type_select_options[0]

    elif category_select.value == "Foreign Trade":
        try:
            type_select_options = mapping_dict["Monthly" + sector_select.value]
            type_select.options = type_select_options

            if type_select.value not in type_select_options:
                type_select.value = type_select_options[0]

            cat1_select_options = mapping_dict[
                "Monthly" + unit_select.value + type_select.value + unit_select.value
            ]
            cat1_select.options = cat1_select_options

            if cat1_select.value not in cat1_select_options:
                cat1_select.value = cat1_select_options[0]

        except Exception as e:
            cat1_select.options = [""]
            cat1_select.value = cat1_select.options[0]


def update_type_select(attrname, old, new):
    if category_select.value == "National Accounts":
        freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
        cat1_select_options = mapping_dict[freq_sect_str + unit_select.value + type_select.value]
        cat1_select.options = cat1_select_options

        if cat1_select.value not in cat1_select_options:
            cat1_select.value = cat1_select_options[0]

    elif category_select.value == "Foreign Trade":
        unit_select_options = mapping_dict["Monthly" + sector_select.value + type_select.value]
        unit_select.options = unit_select_options

        if unit_select.value not in unit_select_options:
            unit_select.value = unit_select_options[0]

        cat1_select_options = mapping_dict[
            "Monthly" + sector_select.value + type_select.value + unit_select.value
        ]
        cat1_select.options = cat1_select_options
        if cat1_select.value not in cat1_select_options:
            cat1_select.value = cat1_select_options[0]


def update_cat1_select(attrname, old, new):
    freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
    if category_select.value == "National Accounts":
        try:
            cat2_select_options = mapping_dict[
                freq_sect_str + unit_select.value + type_select.value + cat1_select.value
            ]
            cat2_select.options = cat2_select_options

            if cat2_select.value not in cat2_select_options:
                cat2_select.value = cat2_select_options[0]

        except Exception as e:
            cat2_select.options = [""]
            cat2_select.value = cat2_select.options[0]

    if category_select.value == "Foreign Trade":
        try:
            cat2_select_options = mapping_dict[
                "Monthly" + sector_select.value + type_select.value + unit_select.value + cat1_select.value
            ]
            cat2_select.options = cat2_select_options

            if cat2_select.value not in cat2_select_options:
                cat2_select.value = cat2_select_options[0]

        except Exception as e:
            cat2_select.options = [""]
            cat2_select.value = cat2_select.options[0]


def update_cat2_select(attrname, old, new):
    freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
    if category_select.value == "National Accounts":
        try:
            cat3_select_options = mapping_dict[
                freq_sect_str + unit_select.value + type_select.value + cat1_select.value + cat2_select.value
            ]
            cat3_select.options = cat3_select_options

            if cat3_select.value not in cat3_select_options:
                cat3_select.value = cat3_select_options[0]

        except Exception as e:
            cat3_select.options = [""]
            cat3_select.value = cat3_select.options[0]

    
    if category_select.value == "Foreign Trade":
        try:
            cat3_select_options = mapping_dict[
                "Monthly" + sector_select.value + type_select.value + unit_select.value + cat1_select.value + cat2_select.value
            ]
            cat3_select.options = cat3_select_options

            if cat3_select.value not in cat3_select_options:
                cat3_select.value = cat3_select_options[0]

        except Exception as e:
            cat3_select.options = [""]
            cat3_select.value = cat3_select.options[0]



def update_cat3_select(attrname, old, new):
    freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
    if category_select.value == "National Accounts":
        try:
            cat4_select_options = mapping_dict[
                freq_sect_str
                + unit_select.value
                + type_select.value
                + cat1_select.value
                + cat2_select.value
                + cat3_select.value
            ]
            cat4_select.options = cat4_select_options

            if cat4_select.value not in cat4_select_options:
                cat4_select.value = cat4_select_options[0]
        except Exception as e:
            cat4_select.options = [""]
            cat4_select.value = cat4_select.options[0]

    if category_select.value == "Foreign Trade":
        try:
            cat4_select_options = mapping_dict[
                "Monthly"
                + sector_select.value
                + type_select.value
                + unit_select.value
                + cat1_select.value
                + cat2_select.value
                + cat3_select.value
            ]
            cat4_select.options = cat4_select_options

            if cat4_select.value not in cat4_select_options:
                cat4_select.value = cat4_select_options[0]
        except Exception as e:
            cat4_select.options = [""]
            cat4_select.value = cat4_select.options[0]


def update_cat4_select(attrname, old, new):
    freq_sect_str = make_freq_sect_str(freq_select.value, sector_select.value)
    if category_select.value == "National Accounts":
        try:
            cat5_select_options = mapping_dict[
                freq_sect_str
                + unit_select.value
                + type_select.value
                + cat1_select.value
                + cat2_select.value
                + cat3_select.value
                + cat4_select.value
            ]
            cat5_select.options = cat5_select_options

            if cat5_select.value not in cat5_select_options:
                cat5_select.value = cat5_select_options[0]
        except Exception as e:
            cat5_select.options = [""]
            cat5_select.value = cat5_select.options[0]

        update_selects_format()

    if category_select.value == "Foreign Trade":
        try:
            cat5_select_options = mapping_dict[
                "Monthly"
                + sector_select.value
                + type_select.value
                + unit_select.value
                + cat1_select.value
                + cat2_select.value
                + cat3_select.value
                + cat4_select.value
            ]
            cat5_select.options = cat5_select_options

            if cat5_select.value not in cat5_select_options:
                cat5_select.value = cat5_select_options[0]
        except Exception as e:
            cat5_select.options = [""]
            cat5_select.value = cat5_select.options[0]

        update_selects_format()

def update_axis_position(attrname, old, new):  # Use to adjust background image position
    global main_p

    x_start = main_p.extra_x_ranges["bi"].start
    x_end = main_p.extra_x_ranges["bi"].end

    y_start = main_p.extra_y_ranges["bi"].start
    y_end = main_p.extra_y_ranges["bi"].end


    for i in main_p.renderers:
        if i.name == "bi":
            i.glyph.y = y_start
            i.glyph.x = x_start
            i.glyph.dh = y_end - y_start
            i.glyph.dw = x_end - x_start

    update_main_axis_range()


def update_main_axis_range(attrname=None, old=None, new=None, expand_perc=1.2):
    global main_p, source
    x_start = main_p.x_range.start
    x_end = main_p.x_range.end
    try:
        x_end = x_end.timestamp()
        x_end = dt.fromtimestamp(int(x_end)) - td(hours=8)
    except Exception as e:
        x_end = dt.fromtimestamp(int(x_end) / 1000) - td(hours=8)
    try:
        x_start = x_start.timestamp()
        x_start = dt.fromtimestamp(int(x_start)) - td(hours=8)
    except Exception as e:
        x_start = dt.fromtimestamp(int(x_start) / 1000) - td(hours=8)

    used_columns = [
        renderer.name for renderer in main_p.renderers if (renderer.visible and renderer.name != "bi")
    ]  # might need to replace with renderer.glyph.y or renderer.glyph.top
    source_df = pd.DataFrame(source.data).set_index("Date")[used_columns]
    source_df_plot = source_df.loc[(source_df.index > x_start) & (source_df.index < x_end)].astype(float)
    new_y_range_end = source_df_plot.max().max()
    new_y_range_start = source_df_plot.min().min()
    new_y_range_end = (
        new_y_range_end * expand_perc if new_y_range_end > 0 else new_y_range_end * (1 - (expand_perc - 1))
    )
    new_y_range_start = (
        new_y_range_start * (1 - (expand_perc - 1)) if new_y_range_start > 0 else new_y_range_start * expand_perc
    )

    main_p.y_range.start = new_y_range_start
    main_p.y_range.end = new_y_range_end
    main_p.y_range.reset_start = new_y_range_start
    main_p.y_range.reset_end = new_y_range_end


def add_button_callback():
    freq_sect_str = ''
    if sector_select.value == 'Deflator':
        freq_sect_str += 'Deflator '
    elif sector_select.value == 'Nominal':
        freq_sect_str += 'NGDP '
    elif sector_select.value == 'Real':
        freq_sect_str += 'RGDP '
    freq_sect_str += freq_select.value

    col_name = f"{tool.get_column_by_selects(country_select, freq_select, sector_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select, category_len=setting.category_structure[category_select.value]['length'])}_{country_select.value}"
    if country_select.value == "TW" and "Taiwan" not in col_name:
        col_name = "Taiwan, " + col_name
    if country_select.value == "CN" and "China" not in col_name:
        col_name = "China, " + col_name
    if country_select.value == "KR" and "Korea" not in col_name:
        col_name = "Korea, " + col_name
    if country_select.value == "JP" and "Japan" not in col_name:
        col_name = "Japan, " + col_name
    data_setting_object = tool.create_data_setting_object(data_setting, col_name)
    old_multichoice_values = multichoice.value

    new_value = (f"{data_setting_object['name']}", data_setting_object["display_name"])
    if new_value not in multichoice.options:
        new_option = multichoice.options
        new_option.append(new_value)
        multichoice.options = new_option

        multichoice.value = old_multichoice_values + [new_value[0]]

    else:
        ctypes.windll.user32.MessageBoxW(0, "Duplicated add, please use the dropdown next to \"Dowload\" to select the desired preset", "ALERT", 48, 0x00001000)
        print("Duplicated Add")



def download_button_callback():
    pass


def index_toggle_callback(active):
    # renew starting date
    global source, main_p, sub_p, datatable, main_p
    main_p.yaxis.axis_label = "Index for " + index_date_input.value
    if pd.DataFrame(source.data).empty:
        return
    source, index_ref_date = tool.update_index_source(source=source, index_date_input_value=index_date_input.value)
    source_dict = dict(pd.DataFrame(source.data).set_index("Date").dropna(how="all", axis=0).reset_index())

    index_date_input.value = index_ref_date

    for p in [main_p, sub_p]:
        for renderer in p.renderers:
            if renderer.name == "bi":
                continue
            else:
                renderer.data_source.data = source_dict
                if "_index" in renderer.name:
                    renderer.visible = active
                else:
                    renderer.visible = not active
    # 1.Data table
    datatable.source.data = source_dict
    current_datatable_columns = datatable.columns
    new_datatable_columns = []
    if active:
        for i in current_datatable_columns:
            col_name = i.field
            if col_name == "Date" or "_index" in col_name:
                new_datatable_columns.append(i)
            else:
                display_name = tool.data_setting_backup.loc[col_name, "display_name"]
                new_column = TableColumn(
                    field=f"{col_name}_index",
                    title=display_name + " (in index)",
                    formatter=NumberFormatter(format="0,0.0"),
                )
                new_datatable_columns.append(new_column)
    else:
        for i in current_datatable_columns:
            col_name = "_".join(i.field.split("_")[:-1])

            if "_index" in i.field:
                data_type = tool.data_setting_backup.loc[col_name, "data_type"]
                display_name = tool.data_setting_backup.loc[col_name, "display_name"]
                if data_type == "p":
                    new_column = TableColumn(
                        field=col_name, title=display_name, formatter=NumberFormatter(format="0.0")
                    )
                elif data_type == "r":
                    new_column = TableColumn(
                        field=col_name, title=display_name, formatter=NumberFormatter(format="0,0.0")
                    )
                new_datatable_columns.append(new_column)
            else:
                new_datatable_columns.append(i)
    datatable.columns = new_datatable_columns

    # 2.tooltips
    new_tooltips = []
    current_tooltips = list(main_p.hover.tooltips)
    if active:
        for i in current_tooltips:

            if "Date" in i[1] or "_index" in i[1]:
                new_tooltips.append(i)
            else:
                col_name = i[1].split("}")[0][2:]
                display_name = tool.data_setting_backup.loc[col_name, "display_name"]
                tooltips_str = "@{" + col_name + "_index" + "}{0.0}"
                new_tooltip = (display_name, tooltips_str)
                main_p.yaxis.formatter = NumeralTickFormatter(format="0,0.0")


                new_tooltips.append(new_tooltip)

    else:
        for i in current_tooltips:

            if "_index" in i[1]:
                col_name = i[1].split("}")[0][2:][:-6]
                data_type = tool.data_setting_backup.loc[col_name, "data_type"]
                display_name = tool.data_setting_backup.loc[col_name, "display_name"]
                if data_type == "p":
                    tooltips_str = "@{" + col_name + "}{0.0}"
                    new_tooltip = (display_name, tooltips_str)
                    main_p.yaxis.formatter = NumeralTickFormatter(format="0.0")

                elif data_type == "r":
                    tooltips_str = "@{" + col_name + "}{0,0.0}"
                    new_tooltip = (display_name, tooltips_str)
                    main_p.yaxis.formatter = NumeralTickFormatter(format="0,0.0")
                new_tooltips.append(new_tooltip)

            else:
                new_tooltips.append(i)

    main_p.hover.tooltips = new_tooltips
    update_main_axis_range()


def multichoice_callback(attr, old, new):
    if len(old) < len(new):
        new_chart(old=old, new=new)
    else:
        drop_chart(old=old, new=new)


def new_chart(old, new):
    global source, main_p, index_date_input, index_toggle
    new = list(set(new) - set(old))[0]
    if new in tool.source_backup.columns.tolist():
        status = False
    else:
        status = True
    data_setting_object = tool.create_data_setting_object(data_setting=data_setting, col_name=new)
    source, index_ref_date = tool.add_source_column(
        source=source, col_name=new, index_date_input_value=index_date_input.value
    )
    source_dict = dict(pd.DataFrame(source.data).set_index("Date").dropna(how="all", axis=0).reset_index())
    index_date_input.value = index_ref_date
    # Condition 1 : new value
    color_set_check = False
    for obj in setting.colors:
        if not obj["used"]:
            color = obj["color"]
            obj["used"] = True
            color_set_check = True
            break
    if (not color_set_check):
        ctypes.windll.user32.MessageBoxW(0, "Maximum charts reached, please remove a chart before adding a new one.", "ALERT", 48, 0x00001000)
        del multichoice.options[-1]

    # plot new object
    if data_setting_object["chart_type"] == "line":
        main_p.line(
            x="Date",
            y=new,
            source=source,
            name=new,
            width=setting.line_width,
            legend_label=data_setting_object["display_name"],
            color=color,
        )
        sub_p.line(x="Date", y=new, source=source, name=new, width=setting.line_width, color=color)

        main_p.line(
            x="Date",
            y=f"{new}_index",
            source=source,
            name=f"{new}_index",
            width=setting.line_width,
            legend_label=data_setting_object["display_name"],
            color=color,
        )
        sub_p.line(
            x="Date", y=f"{new}_index", source=source, name=f"{new}_index", width=setting.line_width, color=color
        )

    elif data_setting_object["chart_type"] == "bar":
        main_p.vbar(
            x="Date",
            top=new,
            source=source,
            name=new,
            width=setting.bar_width,
            line_width=setting.bar_border_color,
            legend_label=data_setting_object["display_name"],
            fill_color=color,
        )

        sub_p.vbar(
            x="Date",
            top=new,
            source=source,
            name=new,
            width=setting.bar_width,
            line_width=setting.bar_border_color,
            fill_color=color,
        )

        main_p.vbar(
            x="Date",
            top=f"{new}_index",
            source=source,
            name=f"{new}_index",
            width=setting.bar_width,
            line_width=setting.bar_border_color,
            legend_label=data_setting_object["display_name"],
            fill_color=color,
        )

        sub_p.vbar(
            x="Date",
            top=f"{new}_index",
            source=source,
            name=f"{new}_index",
            width=setting.bar_width,
            line_width=setting.bar_border_color,
            fill_color=color,
        )

    for p in [main_p, sub_p]:
        for renderer in p.renderers:
            if renderer.name == "bi":
                continue
            elif "_index" in renderer.name:
                renderer.visible = bool(index_toggle.active)
            else:
                renderer.visible = not bool(index_toggle.active)

    new_columns = datatable.columns
    if index_toggle.active:      #change to "if index_toggle.active:" for index button
        new_columns.append(
            TableColumn(
                field=f"{new}_index",
                title=data_setting_object["display_name"] + " (in index)",
                formatter=NumberFormatter(format="0,0.0"),
            )
        )
        main_p.yaxis.axis_label = "Index"
    else:
        if data_setting_object["data_type"] == "p":
            new_columns.append(
                TableColumn(
                    field=new, 
                    title=data_setting_object["display_name"], 
                    formatter=NumberFormatter(format="0.0")
                )
            )
            main_p.yaxis.axis_label = "Value in Billions"
        elif data_setting_object["data_type"] == "b":
            new_columns.append(
                TableColumn(
                    field=new, 
                    title=data_setting_object["display_name"] + " (in billions)", 
                    formatter=NumberFormatter(format="0,0.0")
                )
            )
            main_p.yaxis.axis_label = "Value in Billions"
        elif data_setting_object["data_type"] == "r":
            new_columns.append(
                TableColumn(
                    field=new, 
                    title=data_setting_object["display_name"] + " (in billions)", 
                    formatter=NumberFormatter(format="0,0.0")
                )
            )
            main_p.yaxis.axis_label = "Value in Billions"
        else:
            new_columns.append(
                TableColumn(
                    field=new, 
                    title=data_setting_object["display_name"], 
                    formatter=NumberFormatter(format="0,0.0")
                )
            )
    datatable.columns = new_columns
    datatable.source.data = source_dict

    # add new tooltips
    new_tooltips_list = list(main_p.hover.tooltips)
    if index_toggle.active:
        tooltips_str = "@{" + new + "_index" + "}{0.0}"
        new_tooltips_list.append((data_setting_object["display_name"], tooltips_str))
        main_p.yaxis.formatter = NumeralTickFormatter(format="0,0.0")
    else:
        if data_setting_object["data_type"] == "p":
            tooltips_str = "@{" + new + "}{0.0}"
            new_tooltips_list.append((data_setting_object["display_name"], tooltips_str))
            main_p.yaxis.formatter = NumeralTickFormatter(format="0,0.0")

        if data_setting_object["data_type"] == "r":
            tooltips_str = "@{" + new + "}{0,0}"
            new_tooltips_list.append((data_setting_object["display_name"], tooltips_str))
            main_p.yaxis.formatter = NumeralTickFormatter(format="0,0")
    main_p.hover.tooltips = new_tooltips_list

    for i in main_p.renderers: 
        if i.name == "bi":
            continue
        i.data_source.data = source_dict
    update_main_axis_range()


def drop_chart(old, new):
    global main_p, sub_p, source, datatable
    drop = list(set(old) - set(new))[0]

    for p in [main_p, sub_p]:
        new_renderers_list = []
        renderers_list = list(p.renderers)
        for i, renderer in enumerate(renderers_list):
            if drop in renderer.name:
                try:
                    used_color = renderer.glyph.line_color
                except Exception as e:
                    used_color = renderer.glyph.fill_color
            else:
                new_renderers_list.append(renderer)
        p.renderers = new_renderers_list

    # delete in source and datatable also delete in color dict

    datatable_columns_list = list(datatable.columns)
    for i, column in enumerate(datatable_columns_list):
        if drop in column.field:
            datatable_columns_list.remove(column)
    datatable.columns = datatable_columns_list

    # reset source
    source_df = pd.DataFrame(source.data)
    drop_columns = [i for i in source_df.columns if drop in i]
    source_df = source_df.drop(drop_columns, axis=1).set_index("Date").dropna(how="all", axis=0)
    source = ColumnDataSource(source_df)
    source_dict = dict(source_df.reset_index())

    datatable.source.data = source_dict

    # need to get data_setting object to determine display name
    drop_display_name = tool.data_setting_backup.loc[drop, "display_name"]
    legend_items_list = list(main_p.legend.items)
    for i, item in enumerate(legend_items_list):
        if item.label.value == drop_display_name:
            legend_items_list.remove(item)
    main_p.legend.items = legend_items_list

    for color in setting.colors:
        if color["color"] == used_color:
            color["used"] = False

    for p in [main_p, sub_p]:
        for i in p.renderers:  # in order to prevent
            if i.name == "bi":
                continue
            i.data_source.data = source_dict
    update_main_axis_range()

    new_tooltips_list = list(main_p.hover.tooltips)
    for i in new_tooltips_list:
        if drop in i[1]:
            new_tooltips_list.remove(i)
            break
    main_p.hover.tooltips = new_tooltips_list


def link_callback():
    country_select.on_change(
        "value",
        update_country_select,
        update_category_select,
        update_freq_select,
        update_unit_select,
        update_type_select,
        update_cat1_select,
        update_cat2_select,
        update_cat3_select,
        update_cat4_select,
    )
    category_select.on_change(
        "value",
        update_category_select,
        update_freq_select,
        update_unit_select,
        update_type_select,
        update_cat1_select,
        update_cat2_select,
        update_cat3_select,
        update_cat4_select,
    )
    freq_select.on_change(
        "value",
        update_freq_select,
        update_sector_select,
        update_unit_select,
        update_type_select,
        update_cat1_select,
        update_cat2_select,
        update_cat3_select,
        update_cat4_select,
    )
    sector_select.on_change(
        "value",
        update_freq_select,
        update_unit_select,
        update_type_select,
        update_cat1_select,
        update_cat2_select,
        update_cat3_select,
        update_cat4_select,
    )
    unit_select.on_change(
        "value",
        update_unit_select,
        update_type_select,
        update_cat1_select,
        update_cat2_select,
        update_cat3_select,
        update_cat4_select,
    )
    type_select.on_change(
        "value", update_type_select, update_cat1_select, update_cat2_select, update_cat3_select, update_cat4_select
    )
    cat1_select.on_change("value", update_cat1_select, update_cat2_select, update_cat3_select, update_cat4_select)
    cat2_select.on_change("value", update_cat2_select, update_cat3_select, update_cat4_select)
    cat3_select.on_change("value", update_cat3_select, update_cat4_select)
    cat4_select.on_change("value", update_cat4_select)

    main_p.x_range.on_change("start", update_axis_position)
    main_p.extra_y_ranges["bi"].on_change("start", update_axis_position)
    
    multichoice.on_change("value", multichoice_callback)
    
    add_button.on_click(handler=add_button_callback)
    index_toggle.on_click(handler=index_toggle_callback)


# =========CREATE SELECTS=========
(
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
) = tool.create_selects()
mapping_dict = tool.mapping_dict
mapping = tool.general_mapping
matched_columns = tool.matched_columns
freq_sect_str = ''
if sector_select.value == 'Deflator':
    freq_sect_str += 'Deflator '
elif sector_select.value == 'Nominal':
    freq_sect_str += 'NGDP '
elif sector_select.value == 'Real':
    freq_sect_str += 'RGDP '
freq_sect_str += freq_select.value

for i in setting.freq_data_mapping_map.keys():
    if freq_sect_str in setting.freq_data_mapping_map[i]:
        data, data_setting = tool.read_data(
            data_path=setting.structure[country_select.value][category_select.value][
                f"{setting.freq_full_name_map[i]}_data_path"
            ],
            setting_path=setting.structure[country_select.value][category_select.value][
                f"{setting.freq_full_name_map[i]}_setting_path"
            ],
            matched_columns=matched_columns,
        )
        break

# =========CREATE GLOBAL OBJECTS=========

source = ColumnDataSource(pd.DataFrame())

hover = HoverTool(tooltips=[("Date", "@Date{%F}")], formatters={"@Date": "datetime"}, mode="vline", line_policy="next")

main_p = figure(
    width=setting.figure_width,
    height=setting.figure_height,
    x_axis_type="datetime",
    tools=[PanTool(), hover, ResetTool(), BoxZoomTool(), WheelZoomTool()],
    x_range=(data.index[x_range_start_index], data.index[x_range_end_index]),
    y_range=Range1d(),
)
main_p.yaxis.formatter.use_scientific = False

backgroun_image, xdim, ydim, dim = tool.create_rgba_from_file(path=setting.background_image_path)

main_p.extra_x_ranges = {"bi": Range1d(start=0, end=1)}
main_p.extra_y_ranges = {"bi": Range1d(start=0, end=ydim / xdim)}
main_p.image_rgba(
    image=[backgroun_image],
    x=0,
    y=0,
    dw=1,
    dh=ydim / xdim,
    alpha=0.1,
    level="overlay",
    y_range_name="bi",
    x_range_name="bi",
    name="bi",
)

sub_p = figure(
    width=main_p.width,
    height=setting.range_height,
    y_range=main_p.y_range,
    x_axis_type="datetime",
    y_axis_type=None,
    tools="",
)

range_tool = RangeTool(x_range=main_p.x_range)
range_tool.overlay.fill_color = "forestgreen"
range_tool.overlay.fill_alpha = 0.2

sub_p.add_tools(range_tool)

datatable_columns = [TableColumn(field="Date", title="Date", formatter=DateFormatter())]

datatable = DataTable(
    source=source,
    columns=datatable_columns,
    width=int(setting.datatable_column_width * len(datatable_columns)),
    height=main_p.height + sub_p.height,
    stylesheets=[setting.datatable_stylesheet],
    index_position=None,
)

# =========CREATE BUTTON=========
add_button = Button(
    label="Add",
    width=setting.button_width,
    icon=TablerIcon("circle-plus", size="1.2em"),
    button_type="primary",
    stylesheets=[setting.button_stylesheet],
    height_policy="fit",
    width_policy="fit",
)

download_button = Button(
    label="Download",
    width=setting.button_width,
    icon=TablerIcon("download", size="1.2em"),
    button_type="primary",
    stylesheets=[setting.button_stylesheet],
    height_policy="fit",
    width_policy="fit",
)

index_toggle = Toggle(
    label="Index",
    width=setting.button_width,
    icon=TablerIcon("arrows-exchange-2", size="1.2em"),
    button_type="primary",
    stylesheets=[setting.button_stylesheet],
    height_policy="fit",
    width_policy="fit",
)
multichoice = MultiChoice(
    value=[], options=[], width=setting.multichoice_width, stylesheets=[setting.select_stylesheet]
)

index_date_input = TextInput()

# =========CONSTRUCT LAYOUT=========
layout = column(
    row(
        column(country_select, category_select, freq_select, sector_select),
        column(unit_select, type_select, cat1_select, cat2_select),
        column(cat3_select, cat4_select, cat5_select),
    ),
    row(column(row(add_button, download_button), row(index_toggle, index_date_input)), multichoice),
    row(column(main_p, sub_p), column(datatable)),
)

# Link select and callback
link_callback()
update_selects_format()

curdoc().theme = Theme(filename=setting.theme_file_path)
curdoc().add_root(layout)
curdoc().title = setting.curdoc_name

index_toggle_callback(True)