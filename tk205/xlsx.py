import openpyxl
import os
import json

def resolve_ref(ref, schema_path):
    ref_file_name = ref.split('#')[0]
    if len(ref_file_name) != 0:
        schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205','schema',ref_file_name)
    ref_node_string = ref.split('#/')[1]
    ref_nodes = ref_node_string.split('/')
    base_node = json.load(open(schema_path, "r"))
    ref_node = base_node
    for node in ref_nodes:
        ref_node = ref_node[node]

    return ref_node, schema_path

def traverse_node(rs, ws, schema_path, node, level, row):
    for item in node:
        if item != '$ref':
            ws.cell(row=row, column=level).value = item
            row +=1
        if 'type' in node[item]:
            if node[item]['type'] == 'object':
                row = traverse_node(rs, ws, schema_path, node[item]['properties'], level + 1, row)
        elif 'oneOf' in node[item]:
            if item == 'RS_instance':
                for option in node[item]['oneOf']:
                    if rs in option['$ref']:
                        row = traverse_node(rs, ws, schema_path, option, level, row)
            else:
                for option in node[item]['oneOf']:
                    row = traverse_node(rs, ws, schema_path, option, level, row)
        elif item == '$ref':
            new_node, new_schema_path = resolve_ref(node[item], schema_path)
            row = traverse_node(rs, ws, new_schema_path, new_node['properties'], level + 1, row)
        elif '$ref' in node[item]:
            new_node, new_schema_path = resolve_ref(node[item]['$ref'], schema_path)
            if 'type' in new_node:
                if new_node['type'] == 'object':
                    row = traverse_node(rs, ws, new_schema_path, new_node['properties'], level + 1, row)
        else:
            print(f'Unknown type found in schema: {node[item]}')
    return row

def template(repspec, directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = repspec
    schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
    with open(schema_path, "r") as schema_file:
        schema = json.load(schema_file)
        node = schema['properties']
        level = 1
        row = 1
        traverse_node(repspec, ws, schema_path, node, level, row)
    wb.save(os.path.join(directory,f"{repspec}-template.xlsx"))