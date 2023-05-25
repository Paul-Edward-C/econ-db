# ====================================================================================
# Author:David Ding
# Date:2023/02/17
# Purpose:
#
# ====================================================================================

# =========IMPORT PACKAGES==========
from bokeh.models import ColumnDataSource, NumeralTickFormatter, RangeTool, HoverTool, ResetTool, BoxZoomTool, \
    PanTool, DataTable, TableColumn, NumberFormatter, WheelZoomTool, Button, DateFormatter, MultiChoice, CustomJS, Toggle, TablerIcon
# TablerIcon : https://tabler-icons.io/

from bokeh.plotting import figure
from bokeh.themes import Theme
from bokeh.layouts import column, row
import pandas as pd
import numpy as np
from bokeh.io import curdoc
import os

from lib.tools import Tool, Setting


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
    new_len = 10
    for i in selects_list:
        if i.value == "":
            new_len = selects_list.index(i)
            break
            
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
        
    layout.children[0] = new_layout
    
    pass


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
    
    global mapping_dict, category_len
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
    
    print(cat5_select.value)
    
    update_selects_format()


def add_button_callback():
    col_name = f"{tool.get_column_by_selects(country_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select, category_len=setting.category_structure[category_select.value]['length'])}_{country_select.value}"

    data_setting_object = tool.create_data_setting_object(data_setting, col_name)
    old_multichoice_values = multichoice.value

    new_multichoice_value = f"{data_setting_object['name']}_{country_select.value}"
    if (new_multichoice_value, data_setting_object['display_name']) not in multichoice.options:
        new_option = multichoice.options
        new_option.append((new_multichoice_value, data_setting_object['display_name']))
        multichoice.options = new_option
        
        multichoice.value = old_multichoice_values + [new_multichoice_value]
        
    else:
        print("Duplicated Add")
        

def multichoice_callback(attrname, old, new):
    update_format(new_values=update_chart())


def show_mapping_callback():
    for i in p.renderers:
        print(i.name)


def index_toggle_callback(active):
    print(active)


def update_chart():
    # global variable
    global source
    
    # delete old graph
    old_list = []
    keep_list = []
    new_list = []
    
    for i in range(len(p.renderers)):
        try:
            old_list.append((p.renderers[i].name, i,))
            continue
        except AttributeError as e:
            pass
        
        try:
            old_list.append((p.renderers[i].name, i,))
            continue
        except AttributeError as e:
            pass
    
    for i in old_list:  # i is a tuple
        if i[0] in multichoice.value:
            keep_list.append(i[1])
        
        else:  # set colors to False
            try:
                color = p.renderers[i[1]].glyph.line_color
            except AttributeError as e:
                pass
            try:
                color = p.renderers[i[1]].glyph.fill_color
            except AttributeError as e:
                pass
            
            for g in setting.colors:
                if g['color'] == color:
                    g['used'] = False
    
                    
    source_df = pd.DataFrame(source.data)
    if len(source_df) != 0:
        source_df_cols = source_df.columns[[0] + [i+1 for i in keep_list]].tolist()
        print(source_df_cols)
        source_df = source_df[source_df_cols].set_index("Date")
        source = ColumnDataSource(source_df)
    
    p.renderers = list(np.array(p.renderers)[keep_list])
    range_p.renderers = list(np.array(range_p.renderers)[keep_list])
    data_table.columns = list(np.array(data_table.columns)[[0] + [i + 1 for i in keep_list]])
    hover.tooltips = list(map(tuple, np.array(hover.tooltips)[[0] + [i + 1 for i in keep_list]]))

    # prevent first legend condition
    try:
        p.legend.items = list(np.array(p.legend.items)[keep_list])
    except AttributeError as e:
        pass
    
    for i in multichoice.value:
        if i not in [g[0] for g in old_list]:
            new_list.append(i)
            
            # Need to add a data setting backup
            data_setting_object = tool.create_data_setting_object(data_setting, i)
            source = tool.add_source_column(source=source, col_name=i)
            
            if data_setting_object['chart_type'] == "line":
                p.line(x="Date", y=data_setting_object["name"], source=source, name=i, width=setting.line_width, legend_label=data_setting_object["display_name"])
                range_p.line(x="Date", y=data_setting_object['name'], source=source, name=i, width=setting.line_width)
            
            elif data_setting_object['chart_type'] == "bar":
                p.vbar(x="Date", top=data_setting_object['name'], source=source,
                       name=i, width=setting.bar_width,
                       line_width=setting.bar_border_color,
                       legend_label=data_setting_object['display_name'])
                
                range_p.vbar(x="Date", top=data_setting_object['name'], source=source,
                             name=i, width=setting.bar_width,
                             line_width=setting.bar_border_color)
            
            new_columns = data_table.columns
            new_columns.append(TableColumn(field=data_setting_object['name'], title=data_setting_object['display_name'],
                                           formatter=NumberFormatter()))
            data_table.columns = new_columns
            data_table.source = source
            
    p.legend.click_policy = "mute"
    
    return new_list


def update_format(new_values):
    new_tooltips = hover.tooltips
    
    for i in new_values:
        data_setting_object = tool.create_data_setting_object(data_setting, i)
        index = multichoice.value.index(i)
        
        # update color
        for obj in setting.colors:
            if not obj['used']:
                color = obj['color']
                obj['used'] = True
                break
        
        
        # line case
        if data_setting_object['chart_type'] == "line":
            p.renderers[index].glyph.line_color = color
            range_p.renderers[index].glyph.line_color = color
        
        # bar case
        elif data_setting_object['chart_type'] == "bar":
            p.renderers[index].glyph.fill_color = color
            range_p.renderers[index].glyph.fill_color = color
        
        # percentage case
        if data_setting_object['data_type'] == "p":
            
            tooltips_str = "@{" + data_setting_object['name'] + "}{0.00 %}"
            new_tooltips.append((data_setting_object['display_name'], tooltips_str))
            p.yaxis.formatter = NumeralTickFormatter(format='0,0.00%')
            data_table.columns[index + 1].formatter.format = "0,0.00 %"
        
        # Real number case
        elif data_setting_object['data_type'] == "r":
            
            tooltips_str = "@{" + data_setting_object['name'] + "}{0,0.0 a}"
            new_tooltips.append((data_setting_object['display_name'], tooltips_str))
            p.yaxis.formatter = NumeralTickFormatter(format="0,0.0 a")
            data_table.columns[index + 1].formatter.format = "0,0.00 a"
    
    hover.tooltips = new_tooltips
    
    p.y_range.start, p.y_range.end = tool.get_source_limitvalues(pd.DataFrame(source.data))
    p.yaxis.bounds = (p.y_range.start, p.y_range.end)
    print(p.y_range.start, p.y_range.end)
    
    # print(pd.DataFrame(data_table.source.data))
    
    p.legend.location = "top_left"
    

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
    
    multichoice.on_change("value", multichoice_callback)
    
    add_button.on_click(handler=add_button_callback)
    download_button.js_on_click(CustomJS(args={"datatable": data_table}, code=open(setting.download_button_path).read()))
    index_toggle.on_click(handler=index_toggle_callback)

# =========MAIN CODE========
# main()
# =========CREATE BUTTON START=========

country_select, category_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select = tool.create_selects()
mapping_dict = tool.mapping_dict
mapping = tool.general_mapping
matched_columns = tool.matched_columns


# read data

if freq_select.value[-1] == "Q":
    data, data_setting = tool.read_data(
        data_path=setting.structure[country_select.value][category_select.value]['Quarterly_data_path'],
        setting_path=setting.structure[country_select.value][category_select.value]['Quarterly_setting_path'],
        matched_columns=matched_columns
    )
    
elif freq_select.value[-1] == "A":
    data, data_setting = tool.read_data(
        data_path=setting.structure[country_select.value][category_select.value]['Annual_data_path'],
        setting_path=setting.structure[country_select.value][category_select.value]['Annual_setting_path'],
        matched_columns=matched_columns
    )

default_column = f"{tool.get_column_by_selects(country_select, freq_select, unit_select, type_select, cat1_select, cat2_select, cat3_select, cat4_select, cat5_select, category_len=setting.category_structure[category_select.value]['length'])}_{country_select.value}"
default_data_setting_object = tool.create_data_setting_object(data_setting, default_column)

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
multichoice = MultiChoice(value=[f"{default_data_setting_object['name']}_{country_select.value}"],
                          options=[(f"{default_data_setting_object['name']}_{country_select.value}", default_data_setting_object['display_name'])],
                          width=setting.multichoice_width, stylesheets=[setting.select_stylesheet])

# =========CREATE BUTTON END=========
source = ColumnDataSource(pd.DataFrame())

hover = HoverTool(tooltips=[("Date", "@Date{%F}")],
                  formatters={"@Date": "datetime"},
                  mode='vline', line_policy='next')

p = figure(width=setting.figure_width, height=setting.figure_height, x_axis_type="datetime",
           tools=[PanTool(), hover, ResetTool(), BoxZoomTool(), WheelZoomTool()],
           x_range=(data.index[-30], data.index[-1]))


range_p = figure(width=p.width, height=setting.range_height, y_range=p.y_range,
                 x_axis_type='datetime', y_axis_type=None, tools='')

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "forestgreen"
range_tool.overlay.fill_alpha = 0.2

range_p.add_tools(range_tool)
# range_p.toolbar.active_multi = range_tool


data_table_columns = [
    TableColumn(field='Date', title="Date", formatter=DateFormatter())
]
data_table = DataTable(source=source, columns=data_table_columns,
                       width=int(setting.datatable_column_width * len(data_table_columns)),
                       height=p.height + range_p.height,
                       index_position=0,
                       stylesheets=[setting.datatable_stylesheet],
                       autosize_mode="fit_columns",
                       frozen_columns=1)

update_format(new_values=update_chart())

layout = column(row(column(country_select, category_select, freq_select, unit_select), column(type_select, cat1_select, cat2_select), column(cat3_select, cat4_select, cat5_select)),
                row(add_button, download_button, index_toggle, multichoice),
                row(column(p, range_p), data_table))

# Link select and callback
link_callback()

# Change the format of the selects
update_selects_format()

curdoc().theme = Theme(filename=setting.theme_file_path)

curdoc().add_root(layout)
curdoc().title = setting.curdoc_name

