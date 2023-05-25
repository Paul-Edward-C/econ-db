# ====================================================================================
# Author:David Ding
# Date:2023/02/17
# Purpose:
#
# ====================================================================================

# =========IMPORT PACKAGES==========
from bokeh.models import ColumnDataSource, NumeralTickFormatter, RangeTool, HoverTool, ResetTool, BoxZoomTool, \
    PanTool, DataTable, TableColumn, NumberFormatter, WheelZoomTool, Button, DateFormatter, MultiChoice, CustomJS, Toggle, TablerIcon, Range1d
# TablerIcon : https://tabler-icons.io/

from bokeh.core.properties import value
from bokeh.plotting import figure
from bokeh.themes import Theme
from bokeh.layouts import column, row
import pandas as pd
import numpy as np
from bokeh.io import curdoc
import os

from datetime import datetime as dt
import time

from lib.tools import Tool, Setting

from math import floor

# Specify working directory
dir_path = os.path.dirname(os.path.abspath(__file__))
# Change the working directory to the script directory
os.chdir(dir_path)
print(os.getcwd())

# =========GLOBAL VARIABLES=========

setting = Setting()
tool = Tool()

# =========DEFINE FUNCTION=========

def update_selects_format():
    selects_list = [country_select, category_select, freq_select, unit_select, type_select, cat1_select, cat2_select,
                    cat3_select, cat4_select, cat5_select]
    new_len = next((i for i, select in enumerate(selects_list) if select.value == ""), len(selects_list))
    
    if new_len == 6:
        new_layout = row(column(country_select, category_select, freq_select),
                         column(unit_select, type_select, cat1_select),
                         column())
    elif new_len == 7:
        new_layout = row(column(country_select, category_select, freq_select),
                         column(unit_select, type_select, cat1_select),
                         column(cat2_select))
    elif new_len == 8:
        new_layout = row(column(country_select, category_select, freq_select),
                         column(unit_select, type_select, cat1_select),
                         column(cat2_select, cat3_select))
    elif new_len == 9:
        new_layout = row(column(country_select, category_select, freq_select),
                         column(unit_select, type_select, cat1_select),
                         column(cat2_select, cat3_select, cat4_select))
    elif new_len == 10:
        new_layout = row(column(country_select, category_select, freq_select, unit_select),
                         column(type_select, cat1_select, cat2_select),
                         column(cat3_select, cat4_select, cat5_select))
    print(new_len)
    layout.children[0] = new_layout


def update_country_select(attrname, old, new):
    category_select_options = list(setting.structure[country_select.value].keys())
    category_select.options = category_select_options
    if category_select.value not in category_select_options:
        category_select.value = category_select_options[0]
    
    print(category_select.value)


def update_category_select(attrname, old, new):
    # Change to new columns
    os.chdir(dir_path)
    mapping_raw = pd.read_csv(setting.category_structure[category_select.value]["path"])
    mapping_raw = mapping_raw[~mapping_raw[country_select.value].isna()].replace(np.nan, "")
    # print(f"Mapping_raw : {mapping_raw}")
    
    
    category_len = setting.category_structure[category_select.value]["length"]
    
    
    mapping_dict = tool.create_mapping_dict(df=mapping_raw,
                                            keys=mapping_raw.columns[: category_len - 1],
                                            values=mapping_raw.columns[category_len - 1])

    # Create new general mapping and matched columns
    tool.create_matched_columns_and_general_mapping(df=mapping_raw, country=country_select.value, length=setting.category_structure[category_select.value]["length"])
    
    global mapping
    mapping = tool.general_mapping
    
    global matched_columns
    matched_columns = tool.matched_columns
    
    # Create options for next select
    freq_select_options = mapping_raw[mapping_raw.columns[0]].unique().tolist()
    freq_select.options = freq_select_options
    if freq_select.value not in freq_select_options:
        freq_select.value = freq_select_options[0]
    
    print(freq_select.value)


def update_freq_select(attrname, old, new):
    # Change data source and data setting
    global data, data_setting
    
    for i in setting.data_freq_lookup_table.keys():
        if freq_select.value in setting.data_freq_lookup_table[i]:
            data, data_setting = tool.read_data(
                data_path=setting.structure[country_select.value][category_select.value][f'{i}_data_path'],
                setting_path=setting.structure[country_select.value][category_select.value][f'{i}_setting_path'],
                matched_columns=matched_columns
            )
            break
    
    unit_select_options = mapping_dict[freq_select.value]
    unit_select.options = unit_select_options
    
    if unit_select.value not in unit_select_options:
        unit_select.value = unit_select_options[0]
    
    print(unit_select.value)


def update_unit_select(attrname, old, new):
    type_select_options = mapping_dict[freq_select.value + unit_select.value]
    type_select.options = type_select_options
    
    if type_select.value not in type_select_options:
        type_select.value = type_select_options[0]
    print(type_select.value)


def update_type_select(attrname, old, new):
    cat1_select_options = mapping_dict[freq_select.value + unit_select.value + type_select.value]
    cat1_select.options = cat1_select_options
    
    if cat1_select.value not in cat1_select_options:
        cat1_select.value = cat1_select_options[0]
    print(cat1_select.value)


def update_cat1_select(attrname, old, new):
    try:
        cat2_select_options = mapping_dict[freq_select.value + unit_select.value + type_select.value + cat1_select.value]
        cat2_select.options = cat2_select_options
        
        if cat2_select.value not in cat2_select_options:
            cat2_select.value = cat2_select_options[0]
            
    except Exception as e:
        cat2_select.options = [""]
        cat2_select.value = cat2_select.options[0]
    print(cat2_select.value)


def update_cat2_select(attrname, old, new):
    try:
        cat3_select_options = mapping_dict[freq_select.value + unit_select.value + type_select.value + cat1_select.value + cat2_select.value]
        cat3_select.options = cat3_select_options
        
        if cat3_select.value not in cat3_select_options:
            cat3_select.value = cat3_select_options[0]
    
    except Exception as e:
        cat3_select.options = [""]
        cat3_select.value = cat3_select.options[0]
        
    print(cat3_select.value)


def update_cat3_select(attrname, old, new):
    try:
        cat4_select_options = mapping_dict[freq_select.value + unit_select.value + type_select.value + cat1_select.value + cat2_select.value + cat3_select.value]
        cat4_select.options = cat4_select_options
    
        if cat4_select.value not in cat4_select_options:
            cat4_select.value = cat4_select_options[0]
    except Exception as e:
        cat4_select.options = [""]
        cat4_select.value = cat4_select.options[0]
    print(cat4_select.value)


def update_cat4_select(attrname, old, new):
    try:
        cat5_select_options = mapping_dict[freq_select.value + unit_select.value + type_select.value + cat1_select.value + cat2_select.value + cat3_select.value + cat4_select.value]
        cat5_select.options = cat5_select_options
        
        if cat5_select.value not in cat5_select_options:
            cat5_select.value = cat5_select_options[0]
    except Exception as e:
        cat5_select.options = [""]
        cat5_select.value = cat5_select.options[0]
        
    update_selects_format()
    print(cat5_select.value)


def update_axis_position(attrname, old, new):  # Use to adjust background image position
    
    x_start = main_p.x_range.start
    x_end = main_p.x_range.end
    
    # print(x_start, x_end)
    if (type(x_end) is not float) and (type(x_end) is not int):
        x_end = x_end.timestamp()
    
    y_start = main_p.extra_y_ranges['background_image'].start
    y_end = main_p.extra_y_ranges['background_image'].end
    
    main_p.renderers[0].glyph.x = x_start
    
    if (x_end - x_start) > 0:
        main_p.renderers[0].glyph.w = x_end - x_start

    main_p.renderers[0].glyph.y = y_start
    main_p.renderers[0].glyph.h = y_end - y_start
    
    
def add_button_callback():
    col_name = f"{tool.get_column_by_selects(country_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select, category_len=setting.category_structure[category_select.value]['length'])}_{country_select.value}"
    
    data_setting_object = tool.create_data_setting_object(data_setting, col_name)
    old_multichoice_values = multichoice.value
    
    new_value = (f"{data_setting_object['name']}_{country_select.value}", data_setting_object['display_name'])
    if new_value not in multichoice.options:
        new_option = multichoice.options
        new_option.append(new_value)
        multichoice.options = new_option
        
        multichoice.value = old_multichoice_values + [new_value[0]]
    
    else:
        print("Duplicated Add")


def download_button_callback():
    pass


def multichoice_add():
    pass


def multichoice_delete():
    pass
    

def multichoice_callback(attr, old, new):
    if len(old) < len(new):
        new_chart(old=old, new=new)
    else:
        drop_chart(old=old, new=new)
    
    
def new_chart(old, new):
    new = list(set(new) - set(old))[0]
    if new in tool.source_backup.columns.tolist():
        status = False
    else:
        status = True
        
    # Condition 1 : totally new value
    if status:
        pass
    
    # Condition 2 : existing value but re-add
    else:
        pass


def drop_chart(old, new):
    drop = list(set(old) - set(new))[0]
    print(drop)
    pass


def default_chart(source):
    # add data to source
    # update datatable
    # update format from data_setting_object
    source = tool.add_source_column(source=source, col_name=default_column)
    print(source.data)
    
    for obj in setting.colors:
        if not obj['used']:
            color = obj['color']
            obj['used'] = True
            break
    print(color)
    
    if default_data_setting_object['chart_type'] == "line":
        main_p.line(x="Date", y=default_column, source=source, name=i, width=setting.line_width,
               legend_label=default_data_setting_object["display_name"], color=color)
        sub_p.line(x="Date", y=default_column, source=source, name=i, width=setting.line_width, color=color)

    elif default_data_setting_object['chart_type'] == "bar":
        main_p.vbar(x="Date", top=default_column, source=source,
               name=i, width=setting.bar_width,
               line_width=setting.bar_border_color,
               legend_label=default_data_setting_object['display_name'], fill_color=color)
    
        sub_p.vbar(x="Date", top=default_column, source=source,
                     name=i, width=setting.bar_width,
                     line_width=setting.bar_border_color, fill_color=color)
    new_columns = datatable.columns
    new_columns.append(TableColumn(field=default_column, title=default_data_setting_object['display_name'],
                                   formatter=NumberFormatter()))
    datatable.columns = new_columns
    datatable.source = source
    pass


def link_callback():
    country_select.on_change("value", update_country_select, update_category_select, update_freq_select,
                             update_unit_select, update_type_select, update_cat1_select, update_cat2_select,
                             update_cat3_select, update_cat4_select)
    category_select.on_change("value", update_category_select, update_freq_select, update_unit_select,
                              update_type_select, update_cat1_select, update_cat2_select, update_cat3_select,
                              update_cat4_select)
    freq_select.on_change("value", update_freq_select, update_unit_select, update_type_select, update_cat1_select,
                          update_cat2_select, update_cat3_select, update_cat4_select)
    unit_select.on_change("value", update_unit_select, update_type_select, update_cat1_select, update_cat2_select,
                          update_cat3_select, update_cat4_select)
    type_select.on_change("value", update_type_select, update_cat1_select, update_cat2_select, update_cat3_select,
                          update_cat4_select)
    cat1_select.on_change("value", update_cat1_select, update_cat2_select, update_cat3_select, update_cat4_select)
    cat2_select.on_change("value", update_cat2_select, update_cat3_select, update_cat4_select)
    cat3_select.on_change("value", update_cat3_select, update_cat4_select)
    cat4_select.on_change("value", update_cat4_select)
    
    main_p.x_range.on_change("start", update_axis_position)
    multichoice.on_change("value", multichoice_callback)
    add_button.on_click(handler=add_button_callback)

# =========CREATE SELECTS=========
global country_select, category_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select
country_select, category_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select = tool.create_selects()
mapping_dict = tool.mapping_dict
mapping = tool.general_mapping
matched_columns = tool.matched_columns

for i in setting.data_freq_lookup_table.keys():
    if freq_select.value in setting.data_freq_lookup_table[i]:
        data, data_setting = tool.read_data(
            data_path=setting.structure[country_select.value][category_select.value][f'{i}_data_path'],
            setting_path=setting.structure[country_select.value][category_select.value][f'{i}_setting_path'],
            matched_columns=matched_columns
        )
        break
        
# =========DEFAULT COLUMN=========
column_name_in_db = tool.get_column_by_selects(country_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select, category_len=setting.category_structure[category_select.value]['length'])
current_country = country_select.value
default_column = f"{column_name_in_db}_{current_country}"
default_data_setting_object = tool.create_data_setting_object(data_setting, default_column)

# =========CREATE GLOBAL OBJECTS=========
global main_p, sub_p, source_df, hover, datatable, datatable_columns, source

source = ColumnDataSource(pd.DataFrame())

hover = HoverTool(tooltips=[("Date", "@Date{%F}")],
                  formatters={"@Date": "datetime"},
                  mode='vline', line_policy='next')

main_p = figure(width=setting.figure_width, height=setting.figure_height, x_axis_type="datetime",
                tools=[PanTool(), hover, ResetTool(), BoxZoomTool(), WheelZoomTool()],
                x_range=(data.index[-30], data.index[-1]))

main_p.extra_y_ranges = {"background_image": Range1d(start=0, end=1)}
main_p.image_url(value(setting.background_image_url), x=main_p.x_range.start, w=main_p.x_range.end - main_p.x_range.start, y=0, h=1, anchor="bottom_left", alpha=0.1, level='overlay',
                 y_range_name="background_image", name='background_image')

sub_p = figure(width=main_p.width, height=setting.range_height, y_range=main_p.y_range,
               x_axis_type='datetime', y_axis_type=None, tools='')

range_tool = RangeTool(x_range=main_p.x_range)
range_tool.overlay.fill_color = "forestgreen"
range_tool.overlay.fill_alpha = 0.2

sub_p.add_tools(range_tool)

datatable_columns = [
    TableColumn(field='Date', title="Date", formatter=DateFormatter())
]

datatable = DataTable(source=source, columns=datatable_columns,
                      width=int(setting.datatable_column_width * len(datatable_columns)),
                      height=main_p.height + sub_p.height,
                      stylesheets=[setting.datatable_stylesheet], )

# =========CREATE BUTTON=========
global add_button, download_button, index_toggle, multichoice
add_button = Button(label="Add",
                    width=setting.button_width,
                    icon=TablerIcon('circle-plus', size="1.2em"),
                    button_type='primary',
                    stylesheets=[setting.button_stylesheet],
                    height_policy="fit",
                    width_policy="fit"
                    )

download_button = Button(label='Download',
                         width=setting.button_width,
                         icon=TablerIcon('download', size="1.2em"),
                         button_type='primary',
                         stylesheets=[setting.button_stylesheet],
                         height_policy="fit",
                         width_policy="fit"
                         )

index_toggle = Toggle(label="Index",
                      width=setting.button_width,
                      icon=TablerIcon('arrows-exchange-2', size="1.2em"),
                      button_type='primary',
                      stylesheets=[setting.button_stylesheet],
                      height_policy="fit",
                      width_policy="fit"
                      )
multichoice_values = [f"{default_data_setting_object['name']}_{country_select.value}"]
multichoice_options = [(f"{default_data_setting_object['name']}_{country_select.value}", default_data_setting_object['display_name'])]
multichoice = MultiChoice(value=[],
                          options=[],
                          width=setting.multichoice_width, stylesheets=[setting.select_stylesheet])
multichoice.value = multichoice_values
multichoice.options = multichoice_options

# =========CONSTRUCT LAYOUT=========
layout = column(row(column(country_select, category_select, freq_select, unit_select), column(type_select, cat1_select, cat2_select), column(cat3_select, cat4_select, cat5_select)),
                row(add_button, download_button, index_toggle, multichoice),
                row(column(main_p, sub_p), column(datatable)))

# Link select and callback
link_callback()
update_selects_format()
default_chart(source)


curdoc().theme = Theme(filename=setting.theme_file_path)
curdoc().add_root(layout)
curdoc().title = setting.curdoc_name
