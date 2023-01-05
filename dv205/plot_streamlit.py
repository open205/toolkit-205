
import argparse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import path
from pathlib import Path
from io import BytesIO

import json
import cbor2
import yaml

import streamlit as st

import plotly.express as px
# from dash import Dash, dcc, html, Input, Output, MATCH, ALL


# adding ..\tk205  subfolder to the system path to import file.io

# the following is a kludge needed if the toolkit-205 is not installed as a module
# and throws an exception
try:
    import file_io
except:
    from sys import path as syspath
    syspath.insert(1, '../')
    syspath.insert(1, "../schema-205/")
    from tk205 import file_io


def set_ranges(df, axes, plot_opts, frac=0.5):
    """
        read the dropdown outputs from the gui related to ranges
        and generate x, y, and z ranges 
        Inputs include: df = dataframe to use for finding min/max
        axes : list of the columns being used for x, y, and z axes
        plot_opts: list with columns 1 - 3 being the options for range of "full" or "auto"
        output: list of ranges for x, y, and z, in form [min, max] or None for autorange 
    """
    [x, y, z ] = axes[0:3]
    [x_opt, y_opt, z_opt]  = plot_opts[0:3]

    frac = 0.05

    if x_opt == "Auto":
        xrange = None
    else:
        xmin = df[x].min() - frac*abs(df[x].min())
        xmax = df[x].max() + frac*abs(df[x].max())
        xrange = [xmin, xmax]
    if y_opt == "Auto":
            yrange = None
    else:
        ymin = df[y].min() - frac*abs(df[y].min())
        ymax = df[y].max() + frac*abs(df[y].max())
        yrange = [ymin, ymax]

    if z_opt == "Auto":
        zrange = None
    else:
        zmin = df[z].min() - frac*abs(df[z].min())
        zmax = df[z].max() + frac*abs(df[z].max())
        zrange = [zmin, zmax]
    
    return [xrange, yrange, zrange]


def load(uploaded_file):
    ext = path.splitext(uploaded_file.name)[1].lower()
    if (ext == '.json'):
        return json.load(uploaded_file)
    elif (ext == '.cbor'):
        return cbor2.load(uploaded_file)
    # elif (ext == '.xlsx'):
    #     tree = A205XLSXTree()
    #     return tree.load_workbook(input_file_path).get_content()
    elif (ext == '.yaml') or (ext == '.yml'):
        # with open(input_file_path, 'r') as input_file:
        #     return yaml.load(input_file, Loader=yaml.FullLoader)
        return yaml.load(uploaded_file, Loader=yaml.FullLoader)
    else:
        raise Exception(f"Unsupported input \"{ext}\" for \"{uploaded_file.name}\".")


@st.cache
def load_data(filename):
    data = file_io.load(filename)
    return data


# hack the  css 
# https://www.youtube.com/watch?v=OVgPJEMDkak
# st.markdown(
#     """
#     <style> 
#     .stSelectbox{
#     display:flex;
#     align-items: center;
#     width: 400px;
#     },
    
#     </style>
#     """,
#     unsafe_allow_html=True
# )

###  MAIN CODE STARTS HERE  ###


parser = argparse.ArgumentParser(description="Plot 205 RS data file")

parser.add_argument("rs_filename", nargs='?', type=str,  help="rs file to plot")  # nargs='?' makes it optional to give an argument
parser.add_argument("-y", "--yaml", default="rs_vars.yaml",
                    help="select another yaml file of rs variables")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="provide verbose output = each variable")

args = parser.parse_args()
#:wq
#print(args)
# yaml_config_file = args.config

verbose = args.verbose
vprint = print if verbose else lambda *a, **k: None

yaml_vars_filename = args.yaml
vprint(f"YAML Vars Filename = {yaml_vars_filename}")


if args.rs_filename is not None:
    rs_filename = args.rs_filename
    uploaded_file = False
else:
    uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    if args.rs_filename is None:
        # if we got here we didn't give file name at command line and did an upload.
        # we need to parse this separately from a command line load that uses file_io.load
        rs_in = load(uploaded_file)
    else: 
        rs_in = file_io.load(rs_filename)
    
    rs_filename = uploaded_file.name
    vprint(f"RS Filename = {rs_filename}")
    vprint("loaded RS file")
    # load up the actual rs file to plot and the variable dictionary

    # rs_in = file_io.load(args.rs_filename)
    var_dict = file_io.load(yaml_vars_filename)
    # rs_in = load_data(args.rs_filename)
    print(rs_in)

    metadata = rs_in["metadata"]
    description = rs_in["description"]
    perf_elements = rs_in["performance"].keys()
    rs = metadata["schema"]

    perf_maps={}
    for elem in perf_elements:
        if "performance_map_" in elem:
            perf_maps[elem[16::]] = rs_in["performance"][elem]

    # print(perf_maps)
    perf_map_list = list(perf_maps.keys())
    vprint(f"Performance Maps = {perf_map_list}")




    # create the sidebar for data filtering and selecting plot
    with st.sidebar:
        st.title("Data Filter")
        selected_map = st.sidebar.selectbox("Choose Performance Map: ", perf_map_list)
        # st.sidebar.write("Selected Map is: ", selected_map)

        # selected_map = "cooling"
        # selected_perf_map = "performance_map_cooling"

        # get the names of all the grid and lookup variables
        grid_variables = list(perf_maps[selected_map]["grid_variables"].keys())
        lookup_variables = list(perf_maps[selected_map]["lookup_variables"].keys())

        # create lists of the short names + units
        grid_var_names= [ var_dict[rs]["performance_map_" +selected_map]["grid_variables"][var]["viewer_name"] + \
                        " [" + var_dict[rs]["performance_map_" +selected_map]["grid_variables"][var]["units"] + "]" for var in grid_variables]

        lookup_var_names = [ var_dict[rs]["performance_map_" +selected_map]["lookup_variables"][var]["viewer_name"] + \
                        " [" + var_dict[rs]["performance_map_" +selected_map]["lookup_variables"][var]["units"] + "]" for var in lookup_variables]

        # create a dictionary of mappings
        grid_var_dict = {grid_variables[i]: grid_var_names[i] for i in range(len(grid_variables))}
        lookup_var_dict = {lookup_variables[i]: lookup_var_names[i] for i in range(len(lookup_variables))}
        all_var_dict = {**grid_var_dict, **lookup_var_dict}

        # create reverse lookup dictionaries between short names and full variable names
        reverse_grid_dict =  {grid_var_names[i]: grid_variables[i] for i in range(len(grid_variables))}
        reverse_lookup_dict =  {lookup_var_names[i]: lookup_variables[i] for i in range(len(lookup_variables))}
        reverse_all_dict = {**reverse_grid_dict, **reverse_lookup_dict}

        axis_vars=["None"] + list(reverse_all_dict.keys())
        grid_choices=[]
        for var, name in zip(grid_variables, grid_var_names):
            values = ["*"] + perf_maps[selected_map]["grid_variables"][var]
            grid_choices.append(st.selectbox(f'Select {name} values:', values))


    # now expand grid variables and lookup variables into a 2d data frame with 
    # columns of grid and lookup variablesmuch like the xlsx representation of the performance map
    y=[]
    for var in grid_variables:
        # print(selected_map, var)
        # print(perf_maps[selected_map]["grid_variables"][var])
        y.append(perf_maps[selected_map]["grid_variables"][var])
    df = pd.DataFrame(np.array(np.meshgrid(*y)).reshape(len(grid_variables), -1).T, columns = grid_variables)
    y=[]
    for var in lookup_variables:
        y.append(perf_maps[selected_map]["lookup_variables"][var])

    df2 = pd.DataFrame(np.array(y).T, columns=lookup_variables)
    df4 = pd.concat([df, df2], axis=1)

    # create a Valid column and set it equal to True until we have a valid flag in the RS datafile
    df4["Valid"] = True

    # rename the columns to match the short names we are displaying everywhere
    df4.rename(columns=all_var_dict, inplace=True)

    # create a new column of Trues 
    # then use that same column of Trues as the starting point for the filter
    df4["True"] = True
    data_filter = df4["True"]

    # # the filter was derived from grid_var_names so it must be the same size and we can iterate
    # # through both with zip
    for (var, filter) in zip(grid_var_names, grid_choices):
        if filter != "*":
            data_filter = data_filter & (df4[var] == float(filter))

    df4_filt = df4[data_filter].copy()

    # sort by valid so that we always have the order of all False and then all True 
    # which means that symbols and colors will be in the order of False then True
    df4_filt = df4_filt.sort_values(by = "Valid")
    # create a dummy column of a single value 1 to use in sizing markers.
    df4_filt["size"] = 1

    # set symbols and colors for valid and invalid 
    symbol_map = {True:"circle", False:"x"}
    color_map = ["blue", "red"]


    # print(axes_choice)
    # p set the axes ranges from dropdowns
    # [xrange, yrange, zrange] = set_ranges(df4, axes_choice, plot_opts)

    #print(xrange,yrange,zrange)

    # select performance map with streamlit
    st.header(f"File: {args.rs_filename}")
    col1, col2, col3 = st.columns(3) 
    x_choice=col1.selectbox("X Axis Variable", axis_vars,index=1)
    y_choice=col2.selectbox("Y Axis Variable", axis_vars, index=2)
    z_choice=col3.selectbox("Z Axis Variable", axis_vars, index=0)
    

    x_scale = col1.radio("X Scale", ["Auto","Full"],horizontal=True)
    y_scale = col2.radio("Y Scale", ["Auto","Full"],horizontal=True)
    z_scale = col3.radio("Z Scale", ["Auto","Full"],horizontal=True)


    tab1, tab2 = st.tabs(["Table", "Plot"])
    with tab1:
        st.dataframe(df4_filt)

    with tab2:
        line_choice = "None"
        if z_choice == "None":
            if line_choice == "None":
                fig = px.scatter(df4_filt, x=x_choice, y=y_choice,
                                symbol="Valid", symbol_map=symbol_map,
                                color="Valid", color_discrete_sequence=color_map,
                                size="size", size_max=6,
                                hover_data = grid_var_names,
                )
                # ax1 = df4_filt.plot.scatter(x=x_choice, y=y_choice)
            # else:
            #     fig = px.line(df4_filt, x=x_choice, y=y_choice,
            #                     # line_group = plot_opts[0],
            #                     # symbol="Valid", symbol_map=symbol_map,
            #                     # color="Valid", color_discrete_sequence=color_map,
            #                     # # #  size="size", size_max=6,
            #                     # hover_data = grid_var_names,
            #     )


            # fig.update_xaxes(range=xrange)
            # fig.update_yaxes(range=yrange)

        else:
            fig = px.scatter_3d(df4_filt, x=x_choice,  y=y_choice, z=z_choice,
                                # symbol="Valid", symbol_map=symbol_map,
                                # color="Valid", color_discrete_sequence=color_map,
                                # size="size", size_max=10,
                                # hover_data = grid_var_names,
            )
        st.plotly_chart(fig, theme=None, use_container_width=True)
            # fig.update_layout(scene = dict( xaxis = dict(range=xrange), 
            #                                 yaxis = dict(range=zrange),
            #                                 zaxis = dict(range=yrange)
            #                                 )
            # )

# # common plot formatting that is the same between 2d and 3d plots
# fig.update_layout(title_text = t_string,
#                     template = "seaborn",
#                     )



# # # Create the Dash app
# external_stylesheets = [
#     {
#         "href": "https://fonts.googleapis.com/css2?"
#         "family=Lato:wght@400;700&display=swap",
#         "rel": "stylesheet",
#     },
# ]
# app = Dash(__name__, external_stylesheets=external_stylesheets)
# app.title ="205 Data Investigator"
# # # Set up the app layout



# # generate the HTML for the data filter menu
# map_select_menu=[html.H2("Performance Map to Plot",  className="mapselect-label"),
#     # html.Div([
#         dcc.Dropdown(options=perf_map_list, value=perf_map_list[0],
#                      id={"type": "map_select-dropdown", "index" : "map_select_index"}, className="mapselect-item")
#     # ], className="datafilter-dropdown"), 
# ]


# # generate the HTML for the data filter menu from grid variables list
# grid_filter_menu=[html.H3("Data Filters", className="column-title"),]
# for var, name in zip(grid_variables, grid_var_names):
#     values = perf_maps[selected_map]["grid_variables"][var]
    
#     grid_filter_menu.append(
#         html.Div([
#             html.Label(name, className="datafilter-dropdown-label"),
#             dcc.Dropdown(options=values + ["*"], value = "*",
#                          id={"type": "filter-dropdown", "index" : var}, className="datafilter-dropdown-item")
#         ], className="datafilter-dropdown-row"), 
#     )

# # generate html for the axes selection menu
# all_var_names = lookup_var_names + grid_var_names
# xaxis_vars = all_var_names
# yaxis_vars = all_var_names
# zaxis_vars = ["None"] + all_var_names
# axis_vars={"X": xaxis_vars, "Y": yaxis_vars, "Z": zaxis_vars,}

# axes_select_menu = [html.H3("Axes Selection", className="column-title"),]
# for axis in ["X", "Y", "Z"]:
#     axes_select_menu.append(
#         html.Div([
#             html.Label(f'Plot {axis} Quantity:', className="axesselect-dropdown-label"),
#             dcc.Dropdown(id={"type": "axes-dropdown", "index" : f"{axis}axis"},
#                 options=axis_vars[axis], value=axis_vars[axis][0],className="axesselect-dropdown-item",),
#         ], className="axesselect-dropdown-row"),
#     )

# # generate html for the plot options menu
# scale_lst = []
# plotopts_lst = [html.H3("Plot Options (Not Implemented Yet)", className="column-title"),]
# plotopts_lst.append(
#     html.Div([
#             html.Label('Lines:', className="plotoptions-dropdown-label"),
#             dcc.Dropdown(id={"type": "plotopts-dropdown", "index" : "lines"},
#                 options=(["None"] + xaxis_vars), value="None", className="plotoptions-dropdown-item",),
#         ], className="plotoptions-dropdown-row"),
# )
# for axis in ["X", "Y", "Z"]:
#     plotopts_lst.append(
#             html.Div([
#                 html.Label(f'{axis} Axis Scale', className="plotoptions-radio-label"),
#                 dcc.RadioItems(id={"type": "plotopts-dropdown", "index" : f"{axis}scale"},
#                     options = ['Auto', 'full'], value = 'Auto', inline=True , className="plotoptions-radio-buttons"),
#                 ], className="plotoptions-radio-row"),
# )

# app.layout=html.Div([
#         html.Div(children = map_select_menu, className="mapselect-box"),
#         html.Div(children=[
#             html.Div(children = grid_filter_menu, className="datafilters-column"),
#             html.Div(children = axes_select_menu, className="axesselect-column"),
#             html.Div(children = plotopts_lst, className="plotoptions-column"),
#             ], className="allfilters-box"),
#         html.Div([
#         dcc.Graph(id='plot', className="plot-box")
#         ]   , )    
# ])

# @app.callback(
#     Output('plot', "figure"),
#     Input({"type": "map_select-dropdown", "index": ALL}, "value"),
#     Input({"type": "filter-dropdown", "index": ALL}, "value"),
#     Input({"type": "axes-dropdown", "index": ALL}, "value"),
#     Input({"type": "plotopts-dropdown", "index": ALL}, "value"),
# )
# def update_graphs(selected_maps, filters, axes_choice, plot_opts):
#     """
#     function to update 
#     """
#     selected_map = selected_maps[0]
#     # print(grid_variables)

#     # expand grid variables and lookup variables into a 2d data frame with columns of grid and lookup variables
#     # much like the xlsx representation of the performance map
#     y=[]
#     for var in grid_variables:
#         # print(selected_map, var)
#         # print(perf_maps[selected_map]["grid_variables"][var])
#         y.append(perf_maps[selected_map]["grid_variables"][var])
#     df = pd.DataFrame(np.array(np.meshgrid(*y)).reshape(len(grid_variables), -1).T, columns = grid_variables)
#     y=[]
#     for var in lookup_variables:
#         y.append(perf_maps[selected_map]["lookup_variables"][var])

#     df2 = pd.DataFrame(np.array(y).T, columns=lookup_variables)
#     df4 = pd.concat([df, df2], axis=1)

#     # create a Valid column and set it equal to True until we have a valid flag in the RS datafile
#     df4["Valid"] = True

#     # rename the columns to match the short names we are displaying everywhere
#     df4.rename(columns=all_var_dict, inplace=True)

#     # create a new column of Trues 
#     # then use that same column of Trues as the starting point for the filter
#     df4["True"] = True
#     data_filter = df4["True"]

#     # the filter was derived from grid_var_names so it must be the same size and we can iterate
#     # through both with zip
#     for (var, filter) in zip(grid_var_names, filters):
#         if filter != "*":
#             data_filter = data_filter & (df4[var] == float(filter))

#     df4_filt = df4[data_filter].copy()

#     # t_string = "HPDM data with "
#     # for (name, filter) in zip(shortnames, filters):
#     #     t_string = t_string +f"{name}={filter}, "
#     # t_string = t_string[:-2]

#     t_string = f"205 {rs} Data Plot"

#     # sort by valid so that we always have the order of all False and then all True 
#     # which means that symbols and colors will be in the order of False then True
#     df4_filt = df4_filt.sort_values(by = "Valid")
#     # create a dummy column of a single value 1 to use in sizing markers.
#     df4_filt["size"] = 1
    
#     # print(df4_filt)
#     # set symbols and colors for valid and invalid 
#     symbol_map = {True:"circle", False:"x"}
#     color_map = ["blue", "red"]


#     # print(axes_choice)
#     # p set the axes ranges from dropdowns
#     [xrange, yrange, zrange] = set_ranges(df4, axes_choice, plot_opts)

#     #print(xrange,yrange,zrange)
#     # print(df4_filt)

#     line_choice = plot_opts[0]
#     if axes_choice[2] == "None":
#         if line_choice == "None":
#             fig = px.scatter(df4_filt, x=axes_choice[0], y=axes_choice[1],
#                             symbol="Valid", symbol_map=symbol_map,
#                             color="Valid", color_discrete_sequence=color_map,
#                             size="size", size_max=6,
#                             hover_data = grid_var_names,
#             )
#         else:
#             fig = px.line(df4_filt, x=axes_choice[0], y=axes_choice[1],
#                             line_group = plot_opts[0],
#                             symbol="Valid", symbol_map=symbol_map,
#                             color="Valid", color_discrete_sequence=color_map,
#                             # #  size="size", size_max=6,
#                             hover_data = grid_var_names,
#             )


#         fig.update_xaxes(range=xrange)
#         fig.update_yaxes(range=yrange)

#     else:
#         fig = px.scatter_3d(df4_filt, x=axes_choice[0],  y=axes_choice[2], z=axes_choice[1],
#                             symbol="Valid", symbol_map=symbol_map,
#                             color="Valid", color_discrete_sequence=color_map,
#                             size="size", size_max=10,
#                             hover_data = grid_var_names,
#         )
#         fig.update_layout(scene = dict( xaxis = dict(range=xrange), 
#                                         yaxis = dict(range=zrange),
#                                         zaxis = dict(range=yrange)
#                                        )
#         )

#     # common plot formatting that is the same between 2d and 3d plots
#     fig.update_layout(title_text = t_string,
#                       template = "seaborn",
#                       )

#     # fig = px.scatter(x=[0,1], y=[0,1])
#     return fig


# # Run local server
# if __name__ == '__main__':
#     app.run_server(debug=True)
