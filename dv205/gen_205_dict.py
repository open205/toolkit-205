# this file defines a dictionary that has the grid variables, lookup variables, units, and short names for all the RSs

import yaml
import glob
import re

VERBOSE = True

def camel_to_snake_case(camel):
    # From https://www.geeksforgeeks.org/python-program-to-convert-camel-case-string-to-snake-case/
    snake = ''.join(['_'+i.lower() if i.isupper()
               else i for i in camel]).lstrip('_')
    return snake

def extract_itemnames(string):
    substring = string.strip("()").replace("{","").replace("}","").replace(" ","")
    item = substring.split(",")
    return item

def shorten_name(string):
    # routine to shorten a snake case name to first 3 letters of each word

    # do this with pattern matching for a "smart" shortening
    dict={"dry_bulb_temperature": "Tdb",
         "wet_bulb_temperature": "Twb",
         "indoor_coil": "in_coil",
         "outdoor_coil": "out_coil",
         "absolute_air_pressure": "Pabs",
         "mass_flow_rate": "Mdot",
         "volumetric_flow_rate": "Vdot",
         "pressure_difference": "Pdiff",
         "entering": "ent",
         "leaving": "exit",
         "exiting": "exit",
         "ambient": "amb",
         "power": "pow",
         "frequency": "freq",
         "relative_humidity": "RH",
         "indoor": "in",
         "input": "in",
         "outdoor": "out",
         "output": "out",
         "total": "tot",
         "latent": "lat",
         "sensible": "sens",
         "capacity": "cap",
         "environment": "env",
         "compressor": "comp",
         "sequence": "seq",
         "number": "num",
         "rotational": "rot",
         "auxiliary": "aux",
         "evaporator": "evap",
         "condenser": "cond",
         "liquid": "liq",
         "standard": "std",
         "static": "stat",
         "pressure": "pres",
         "difference": "diff",
         "impeller": "imp",
         "efficiency": "eff",

         }
    if VERBOSE: print(string)

    short_string = string
    for word in dict:
        short_string = re.sub(word, dict[word], short_string)
    
    return string  # don't actually shorten
    # return short_string



def extract_variables(rs, map):

    grid_var_list = rs[map]["Data Elements"]["grid_variables"]["Data Type"].strip("{}")

    grid_variables={}

    for var in list(rs[grid_var_list]["Data Elements"].keys()):
        grid_variables[var] = {"units": rs[grid_var_list]["Data Elements"][var]["Units"],
                            "viewer_name": shorten_name(var)}

    lookup_var_list = rs[map]["Data Elements"]["lookup_variables"]["Data Type"].strip("{}")

    lookup_variables={}
    # for var in list(rs[lookup_var_list]["Data Elements"].keys()):
    #     lookup_variables[var] = rs[lookup_var_list]["Data Elements"][var]["Units"]

    for var in list(rs[lookup_var_list]["Data Elements"].keys()):
        lookup_variables[var] = {"units": rs[lookup_var_list]["Data Elements"][var]["Units"],
                            "viewer_name": shorten_name(var)}

    return {"grid_variables": grid_variables, "lookup_variables": lookup_variables}



### MAIN CODE STARTS HERE ###


output_file = "rs_vars.yaml"

# set path to the directory within the toolkit git repository in the submodule
# schema that has the yaml input to the RS schema
dir_path = r"..\schema-205\schema-source\rs*.schema.yaml"
files = glob.glob(dir_path)

rs_list = []
schemas = {}
for file in files:
    with open(file, 'r') as input_file:
        rs = file[-18:][0:6]
        rs_list.append(rs)
        if VERBOSE: print(rs)
        schemas[rs] = yaml.load(input_file, Loader=yaml.FullLoader)


rs_dict = {}
for rs in rs_list:
    rs_dict[rs]={}
    perf_elements = list(schemas[rs]["Performance"]["Data Elements"].keys())
    for element in perf_elements:
        if "performance_map" in element:
            maps = extract_itemnames(schemas[rs]["Performance"]["Data Elements"][element]["Data Type"])
            for map in maps:
                snake_map = camel_to_snake_case(map)
                rs_dict[rs][snake_map]={}
                rs_dict[rs][snake_map]=extract_variables(schemas[rs],map)

with open(output_file, 'w') as out_file:
    yaml.dump(rs_dict, out_file, sort_keys=False)