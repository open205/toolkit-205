import openpyxl
import os
import json
import re
import enum
from .__init__ import validate
from .schema import A205Schema

class SheetType(enum.Enum):
    FLAT = 0
    PERFORMANCE_MAP = 1
    ARRAY = 2


class A205XLSXNode:

    def __init__(self, name, parent=None, tree=None, value=None):
        self.parent = parent
        if parent:
            self.lineage = parent.lineage + [name]
            parent.add_child(self)
            self.tree = parent.tree
            self.first_row = parent.last_row + 1
            self.last_row = self.first_row
            self.increment_parent_rows()
            self.inner_rs = parent.inner_rs
        else:
            # Root node
            self.lineage = [name]
            self.tree = tree
            self.first_row = 2
            self.last_row = 2
            self.inner_rs = self.tree.rs
        self.value = value
        self.children = []
        self.name = name

        self.is_performance_map = "performance_map" in name

        if self.is_performance_map:
            self.sheet = self.tree.rs #name
            self.sheet_type = SheetType.PERFORMANCE_MAP
        else:
            self.sheet = self.tree.rs
            self.sheet_type = SheetType.FLAT

    def add_child(self, node):
        self.children.append(node)

    def get_num_ancestors(self):
        if self.parent:
            return len(self.parent.lineage)
        else:
            return 0

    def increment_parent_rows(self):
        if self.parent:
            self.parent.last_row += 1
            self.parent.increment_parent_rows()

    def write_header(self, worksheet):
        xlsx_headers = ['Data Group', 'Data Element', 'Value', 'Units', 'Required']
        for column, header in enumerate(xlsx_headers, start=1):
            worksheet.cell(row=1, column=column).value = header
            worksheet.cell(row=1, column=column).font = openpyxl.styles.Font(bold=True)
        worksheet.column_dimensions['B'].width = 40
        worksheet.column_dimensions['C'].width = 31

    def get_schema_node(self):
        return self.tree.schema.get_schema_node(self.lineage)

    def is_required(self):
        if self.parent:
            parent_schema_node = self.parent.get_schema_node()
            if 'required' in parent_schema_node:
                return self.name in parent_schema_node['required']
            else:
                return False
        else:
            return True

    def write_node(self):
        wb = self.tree.workbook
        sheet = self.sheet
        if sheet not in wb:
            wb.create_sheet(sheet)
            if self.sheet_type == SheetType.FLAT:
                self.write_header(wb[sheet])    
        
        if len(self.children) > 0:
            value_column = 1
            wb[sheet].cell(row=self.first_row,column=value_column).value = '.'.join(self.lineage)
        else:
            value_column = 2
            wb[sheet].cell(row=self.first_row,column=value_column).value = self.name

        schema_node = self.get_schema_node()

        if schema_node:
            # Add units
            if 'units' in schema_node:
                wb[sheet].cell(row=self.first_row,column=4).value = schema_node['units']

            # Add required
                # TODO: Make conditional formatting (e.g. red name if not entered)
            wb[sheet].cell(row=self.first_row,column=5).value = self.is_required()

            # Add description
            if 'description' in schema_node:
                comment = openpyxl.comments.Comment(schema_node['description'],"ASHRAE 205")
                wb[sheet].cell(row=self.first_row,column=value_column).comment = comment

            # Enum validation
            if 'enum' in schema_node:
                enumerants = f'"{",".join(schema_node["enum"])}"'
                if len(enumerants) < 256: # Apparent limitation of written lists (TODO: https://stackoverflow.com/a/33532984/1344457)
                    dv = openpyxl.worksheet.datavalidation.DataValidation(type='list',formula1=enumerants,allow_blank=True)
                    wb[sheet].add_data_validation(dv)
                    dv.add(wb[sheet].cell(row=self.first_row,column=3))

        else:
            # Not found in schema
            comment = openpyxl.comments.Comment("Not found in schema.","ASHRAE 205")
            wb[sheet].cell(row=self.first_row,column=value_column).comment = comment

        if self.value is not None:
            wb[sheet].cell(row=self.first_row,column=3).value = self.value

        for child in self.children:
            child.write_node()

    def collect_content(self, content):
        if len(self.children) > 0:
            content[self.name] = {}
            for child in self.children:
                child.collect_content(content[self.name])
        else:
            content[self.name] = self.value

    def read_node(self):
        ws = self.tree.workbook[self.sheet]
        end_node = False
        while not end_node:
            data_group = ws.cell(row=self.last_row,column=1).value
            data_element = ws.cell(row=self.last_row,column=2).value
            value = ws.cell(row=self.last_row,column=3).value
            if data_group:
                lineage = data_group.split(".")
                if len(lineage) <= self.get_num_ancestors():
                    # if lineage the same or shorter, this is not going to be a child node
                    end_node = True
                else:
                    new_node = A205XLSXNode(lineage[-1], parent = self)
                    new_node.read_node()
            elif data_element:
                A205XLSXNode(data_element, parent=self, value=value)
            else:
                # End of sheet
                end_node = True

class A205XLSXTree:

    def __init__(self):
        self.content = {}
        self.rs = ""
        self.schema = A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
        self.root_node = None

    def load_workbook(self, file_name):
        '''
        Load contents from XLSX workbook into tree content
        '''
        self.workbook = openpyxl.load_workbook(file_name)
        # Find Primary RS worksheet
        rs_pattern = re.compile("^RS(\\d{4})$")
        for ws in self.workbook:
            if rs_pattern.match(ws.title):
                self.rs = ws.title

        self.root_node = A205XLSXNode("ASHRAE205", tree=self)
        self.root_node.last_row += 1
        self.root_node.read_node()
        return self

    def traverse_content(self, content, parent):
        for item in content:
            if type(content[item]) == dict:
                new_node = A205XLSXNode(item,parent=parent)
                self.traverse_content(content[item], new_node)
            elif type(content[item]) == list:
                A205XLSXNode(item,parent=parent,value="list")
            else:
                A205XLSXNode(item,parent=parent,value=content[item])

    def load(self, content):
        '''
        Load object data into tree content
        '''
        if "ASHRAE205" in content:
            if "RS_ID" in content["ASHRAE205"]:
                self.rs = content["ASHRAE205"]["RS_ID"]
            else:
                raise KeyError("Could not find 'RS_ID' key.")
        else:
            raise KeyError("Could not find 'ASHRAE205' object.")

        self.root_node = A205XLSXNode("ASHRAE205", tree=self)
        self.traverse_content(content["ASHRAE205"], self.root_node)

    def create_tree_from_schema(self, node):
        schema_node = node.get_schema_node()

        if 'RS' in schema_node:
            node.inner_rs = schema_node['RS']

        if 'properties' in schema_node:
            for item in schema_node['properties']:
                self.create_tree_from_schema(A205XLSXNode(item, parent = node))
        
        if 'oneOf' in schema_node:
            if node.name == 'RS_instance':
                self.create_tree_from_schema(A205XLSXNode(node.inner_rs, parent = node))

    def template_tree(self, repspec, **kwargs):
        '''
        Generate empty tree content based on the schema for a specific RS?
        Generate an XLSX template based on the schema for a specific RS.

        kwargs:
          RS0002:
            - grid_var_file = ''
            - fan_rs = False
            - fan_type = discrete
          RS0003
            - grid_var_file = ''
            - fan_type = continuous
        '''
        self.rs = repspec
        self.root_node = A205XLSXNode("ASHRAE205", tree=self)
        self.create_tree_from_schema(self.root_node)


    def template(self, repspec, directory, **kwargs):
        '''
        Generate empty tree content based on the schema for a specific RS?
        Generate an XLSX template based on the schema for a specific RS.

        kwargs:
          RS0002:
            - grid_var_file = ''
            - fan_rs = False
            - fan_type = discrete
          RS0003
            - grid_var_file = ''
            - fan_type = continuous
        '''
        self.template_tree(repspec, **kwargs)
        output_path = os.path.join(directory,f"{repspec}-template.xlsx")
        self.save(output_path)

    def save(self, file_name):
        '''
        Save tree as workbook
        '''
        self.workbook = openpyxl.Workbook()
        
        # Write tree content
        self.workbook.active.title = self.rs
        self.root_node.write_header(self.workbook[self.rs])
        self.root_node.write_node()

        self.workbook.save(file_name)

    def get_content(self):
        '''
        returns tree content
        '''
        content = {}
        self.root_node.collect_content(content)
        return content

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

def template(repspec, directory):
    '''
    Generate an XLSX template based on the schema for a specific RS
    '''
    if not os.path.isdir(directory):
        os.mkdir(directory)
    tree = A205XLSXTree()
    tree.template(repspec,directory)
