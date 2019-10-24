import openpyxl
import os
import json

def resolve_ref(ref, schema_path):
    '''
    Resolves $refs in ASHRAE 205 JSON schema when parsing using a normal JSON parser
    '''
    ref_file_name = ref.split('#')[0]
    if len(ref_file_name) != 0:
        schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205','schema',ref_file_name)
    base_node = json.load(open(schema_path, "r"))
    ref_node = base_node
    if len(ref.split('#/')) > 1:
        ref_node_string = ref.split('#/')[1]
        ref_nodes = ref_node_string.split('/')
        for node in ref_nodes:
            ref_node = ref_node[node]

    return ref_node, schema_path

def create_perf_map_template(wb, node, name):
    if name not in wb:
        wb.create_sheet(name)
    else:
        raise Exception("Duplicate performance map detected: {name}")

    col = 1

    # Grid variables
    var_node = node['grid_variables']['properties']
    for item in var_node:
        wb[name].cell(row=1,column=col).value = item
        wb[name].cell(row=1,column=col).font = openpyxl.styles.Font(color='0070C0')
        wb[name].cell(row=1,column=col).alignment = openpyxl.styles.Alignment(text_rotation=45)
        if 'units' in var_node[item]:
            wb[name].cell(row=2,column=col).value = var_node[item]['units']
        col += 1

    # Lookup variables
    var_node = node['lookup_variables']['properties']
    for item in var_node:
        wb[name].cell(row=1,column=col).value = item
        wb[name].cell(row=1,column=col).alignment = openpyxl.styles.Alignment(text_rotation=45)
        if 'units' in var_node[item]:
            wb[name].cell(row=2,column=col).value = var_node[item]['units']
        col += 1

def traverse_node(rs, wb, schema_path, node, required_items, level, row):
    '''
    Recursive function to write ASHRAE 205 JSON Schema content to an XLSX workbook.
    Recursive calls occur for nested objects and $refs.
    '''
    for item in node:
        if item != '$ref':

            # Special handling of $ref items
            if '$ref' in node[item]:
                node_item, new_schema_path = resolve_ref(node[item]['$ref'], schema_path)
            else:
                node_item = node[item]

            # Write data group/element name
            if 'type' in node_item:
                if node_item['type'] == 'object':
                    wb[rs].cell(row=row, column=1).value = item
                    if 'performance_map' in item:
                        create_perf_map_template(wb, node[item]['properties'], item)
                else:
                    wb[rs].cell(row=row, column=2).value = item
            elif 'oneOf' in node_item:
                wb[rs].cell(row=row, column=1).value = item
                if 'performance_map' in item:
                    for i, option in enumerate(node_item['oneOf']):
                        create_perf_map_template(wb, option['properties'], f"{item} {i}")

            # Write data element units
            if 'units' in node_item:
                wb[rs].cell(row=row, column=4).value = node_item['units']

            # Write if data element is required
            if item in required_items:
                wb[rs].cell(row=row, column=5).value = 'Yes'

            row +=1

        # Handle types within this node
        if 'type' in node[item]:
            # Normal nested data group
            if node[item]['type'] == 'object':
                if 'required' in node[item]:
                    required_items = node[item]['required']

                row = traverse_node(rs, wb, schema_path, node[item]['properties'], required_items, level + 1, row)
        elif 'oneOf' in node[item]:
            # Alternates

            if item == 'RS_instance':
                # Special case for the RS_instance (creates only the template for the corresponding RS)
                for option in node[item]['oneOf']:
                    if rs in option['$ref']:
                        row = traverse_node(rs, wb, schema_path, option, required_items, level, row)
            else:
                # For all other cases create one instance of each
                for option in node[item]['oneOf']:
                    row = traverse_node(rs, wb, schema_path, option['properties'], required_items, level, row)
        elif item == '$ref':
            # $ref items (typically $refs in RS_instance)
            new_node, new_schema_path = resolve_ref(node[item], schema_path)
            row = traverse_node(rs, wb, new_schema_path, new_node['properties'], required_items, level + 1, row)
        elif '$ref' in node[item]:
            # $ref nodes (typically defined enums and embedded representations)
            new_rs = rs
            if 'RS' in node[item]:
                new_rs = node[item]['RS']
                if new_rs not in wb:
                    wb.create_sheet(new_rs)
            new_node, new_schema_path = resolve_ref(node[item]['$ref'], schema_path)
            if 'type' in new_node:
                if new_node['type'] == 'object':
                    row = traverse_node(new_rs, wb, new_schema_path, new_node['properties'], required_items, level + 1, row)
        else:
            raise Exception(f'Unknown type found in schema: {node[item]}')
    return row

def template(repspec, directory):
    '''
    Generate an XLSX template based on the schema for a specific RS
    '''
    if not os.path.isdir(directory):
        os.mkdir(directory)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = repspec
    headers = ['Data Group', 'Data Element', 'Value', 'Units', 'Required']
    for column, header in enumerate(headers, start=1):
        wb[repspec].cell(row=1, column=column).value = header
        wb[repspec].cell(row=1, column=column).font = openpyxl.styles.Font(bold=True)
    schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
    with open(schema_path, "r") as schema_file:
        schema = json.load(schema_file)
        node = schema['properties']
        level = 1
        row = 2
        traverse_node(repspec, wb, schema_path, node, ['ASHRAE205'], level, row)
    wb.save(os.path.join(directory,f"{repspec}-template.xlsx"))