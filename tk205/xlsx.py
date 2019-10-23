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

def traverse_node(rs, ws, schema_path, node, required_items, level, row):
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
                    ws.cell(row=row, column=1).value = item
                else:
                    ws.cell(row=row, column=2).value = item
            elif 'oneOf' in node_item:
                ws.cell(row=row, column=1).value = item

            # Write data element units
            if 'units' in node_item:
                ws.cell(row=row, column=4).value = node_item['units']

            # Write if data element is required
            if item in required_items:
                ws.cell(row=row, column=5).value = 'Yes'

            row +=1

        # Handle types within this node
        if 'type' in node[item]:
            # Normal nested data group
            if node[item]['type'] == 'object':
                if 'required' in node[item]:
                    required_items = node[item]['required']

                row = traverse_node(rs, ws, schema_path, node[item]['properties'], required_items, level + 1, row)
        elif 'oneOf' in node[item]:
            # Alternates

            if item == 'RS_instance':
                # Special case for the RS_instance (creates only the template for the corresponding RS)
                for option in node[item]['oneOf']:
                    if rs in option['$ref']:
                        row = traverse_node(rs, ws, schema_path, option, required_items, level, row)
            else:
                # For all other cases create one instance of each
                for option in node[item]['oneOf']:
                    row = traverse_node(rs, ws, schema_path, option['properties'], required_items, level, row)
        elif item == '$ref':
            # $ref items
            new_rs = rs
            if 'RS' in node:
                new_rs = node['RS']
            new_node, new_schema_path = resolve_ref(node[item], schema_path)
            row = traverse_node(new_rs, ws, new_schema_path, new_node['properties'], required_items, level + 1, row)
        elif '$ref' in node[item]:
            # $ref nodes
            new_rs = rs
            if 'RS' in node[item]:
                new_rs = node[item]['RS']
            new_node, new_schema_path = resolve_ref(node[item]['$ref'], schema_path)
            if 'type' in new_node:
                if new_node['type'] == 'object':
                    row = traverse_node(new_rs, ws, new_schema_path, new_node['properties'], required_items, level + 1, row)
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
        ws.cell(row=1, column=column).value = header
        ws.cell(row=1, column=column).font = openpyxl.styles.Font(bold=True)
    schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
    with open(schema_path, "r") as schema_file:
        schema = json.load(schema_file)
        node = schema['properties']
        level = 1
        row = 2
        traverse_node(repspec, ws, schema_path, node, ['ASHRAE205'], level, row)
    wb.save(os.path.join(directory,f"{repspec}-template.xlsx"))