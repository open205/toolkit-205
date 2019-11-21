import openpyxl
import os
import json
import re
import enum
from .__init__ import validate
from .schema import A205Schema
from .util import process_grid_set, unique_name_with_index

class SheetType(enum.Enum):
    FLAT = 0
    PERFORMANCE_MAP = 1
    ARRAY = 2


class A205XLSXNode:

    white_space_multiplier = 4

    def __init__(self, name, parent=None, tree=None, value=None):
        self.children = []  # List of children A205XLSXNodes
        self.name = name  # Name of this node
        self.value = value  # Value (if any) of this node
        self.parent = parent  # Parent A205XLSXNode of this node
        self.grid_set = None  # Ordered arrays of repeated grid variable values (used only for grid_variable nodes)

        if parent:
            # Inherit much information from parent
            self.lineage = self.parent.lineage + [name]  # List of parent node names (as strings)
            self.tree = self.parent.tree
            self.inner_rs = self.parent.inner_rs
            self.sheet = self.parent.child_sheet
            self.sheet_type = self.parent.child_sheet_type
            self.beg = self.parent.child_beg
            if self.sheet_type == SheetType.FLAT:
                self.child_beg = self.beg + 1
            else:
                self.child_beg = self.beg
        else:
            # Root node
            self.lineage = [name]
            self.tree = tree
            self.inner_rs = self.tree.rs
            self.sheet = self.tree.rs
            self.sheet_type = SheetType.FLAT
            self.child_sheet_type = self.sheet_type
            self.beg = 3
            self.child_beg = 4

        if self.sheet not in self.tree.sheets:
            self.tree.sheets.append(self.sheet)

        # These will be changed by any children
        self.end = self.beg
        self.child_end = self.child_beg

        self.increment_ancestors()

        self.child_sheet = self.sheet
        self.child_sheet_type = self.sheet_type

        # Initial detection of new sheets
        if type(self.value) == str:
            if self.value[0] == "$":
                # Indicator of pointer to another sheet
                if "performance_map" in self.value:
                    self.child_sheet_type = SheetType.PERFORMANCE_MAP
                elif "RS" in self.value:
                    self.child_sheet_type = SheetType.FLAT
                else:
                    self.child_sheet_type = SheetType.ARRAY
                self.child_sheet = self.value[1:]

                if self.child_sheet_type == SheetType.FLAT:
                    self.child_beg = 3
                    self.child_end = 3
                else:
                    self.child_beg = 1
                    self.child_end = 1

        if parent:
            self.parent.add_child(self)

    def add_child(self, node):
        '''
        Add a child node to this node.
        '''
        self.children.append(node)

    def get_num_ancestors(self):
        '''
        Count ancestors back to root.
        '''
        if self.parent:
            return len(self.parent.lineage)
        else:
            return 0

    def get_ancestor(self,generation):
        if generation == 0:
            return self
        else:
            return self.parent.get_ancestor(generation - 1)

    def increment_ancestors(self):
        '''
        Increment the begining and endings appropriately for ancestors
        '''
        if self.parent:
            if self.sheet == self.parent.sheet:
                # If parent is in the same sheet increment both
                self.parent.end = self.end
                self.parent.increment_ancestors()
            self.parent.child_beg = self.end + 1

    def add_grid_set(self, grid_set):
        '''
        Add a cartesian product grid set to this node.

        Only used for "grid_variables" nodes.
        '''
        if self.name != 'grid_variables':
            raise Exception(f"Cannot add a grid set to '{self.name}'. Grid sets can only be added to 'grid_variables' nodes.")
        self.grid_set = grid_set

    def get_schema_node(self):
        '''
        Search for schema content for this node
        '''
        return self.tree.schema.get_schema_node(self.lineage)

    def is_required(self):
        '''
        Check schema if this is a required node
        '''
        if self.parent:
            parent_schema_node = self.parent.get_schema_node()
            if 'required' in parent_schema_node:
                return self.name in parent_schema_node['required']
            else:
                return False
        else:
            return True

    def write_header(self, worksheet):
        '''
        Write the header data for a new sheet
        '''
        if self.parent:
            worksheet.cell(row=1, column=1).value = '.'.join(self.lineage)
            worksheet.cell(row=1, column=1).font = openpyxl.styles.Font(bold=True,sz=14)
        else:
            worksheet.cell(row=1, column=1).value = f"{self.tree.rs}: {self.tree.schema.get_rs_title(self.tree.rs)}"
            worksheet.cell(row=1, column=1).font = openpyxl.styles.Font(bold=True,sz=14)
        if self.sheet_type == SheetType.FLAT:
            xlsx_headers = ['Data Group', 'Data Element', 'Value', 'Units', 'Required']
            for column, header in enumerate(xlsx_headers, start=1):
                worksheet.cell(row=2, column=column).value = header
                worksheet.cell(row=2, column=column).font = openpyxl.styles.Font(bold=True)
            worksheet.column_dimensions['B'].width = 50
            worksheet.column_dimensions['C'].width = 31

    def write_node(self):
        '''
        Write tree content to XLSX
        '''
        wb = self.tree.workbook
        sheet = self.sheet
        if sheet not in wb:
            wb.create_sheet(sheet)
            self.write_header(wb[sheet])

        schema_node = self.get_schema_node()

        # TODO: Hyperlink to sheets from '$' values

        if self.sheet_type == SheetType.FLAT:

            if len(self.children) > 0:
                level_index = 1
                wb[sheet].cell(row=self.beg,column=level_index).value = '.'.join(self.lineage)
            else:
                level_index = 2
                buffer = ' '*(self.get_num_ancestors() - 1)*self.white_space_multiplier
                wb[sheet].cell(row=self.beg,column=level_index).value = buffer + self.name

            if schema_node:
                # Add units
                if 'units' in schema_node:
                    wb[sheet].cell(row=self.beg,column=4).value = schema_node['units']

                # Add required
                    # TODO: Make conditional formatting (e.g. red name if not entered)
                if self.is_required():
                    wb[sheet].cell(row=self.beg,column=5).value = u'\u2713'  # Checkmark
                wb[sheet].cell(row=self.beg,column=5).alignment = openpyxl.styles.Alignment(horizontal='center')

                # Add description
                if 'description' in schema_node:
                    comment = openpyxl.comments.Comment(schema_node['description'],"ASHRAE 205")
                    wb[sheet].cell(row=self.beg,column=level_index).comment = comment

                # Enum validation
                if 'enum' in schema_node:
                    enumerants = f'"{",".join(schema_node["enum"])}"'
                    if len(enumerants) < 256: # Apparent limitation of written lists (TODO: https://stackoverflow.com/a/33532984/1344457)
                        dv = openpyxl.worksheet.datavalidation.DataValidation(type='list',formula1=enumerants,allow_blank=True)
                        wb[sheet].add_data_validation(dv)
                        dv.add(wb[sheet].cell(row=self.beg,column=3))

            else:
                # Not found in schema
                comment = openpyxl.comments.Comment("Not found in schema.","ASHRAE 205")
                wb[sheet].cell(row=self.beg,column=level_index).comment = comment
                wb[sheet].cell(row=self.beg,column=level_index).font = openpyxl.styles.Font(color='FF0001',bold=True)

            if self.value is not None:
                wb[sheet].cell(row=self.beg,column=3).value = self.value

        # TODO: Something better here...a lot of repetition...
        elif self.sheet_type == SheetType.PERFORMANCE_MAP:
            if len(self.children) > 0:
                level_index = 2
            else:
                level_index = 3

            wb[sheet].cell(row=level_index,column=self.beg).value = self.name
            if self.name == 'grid_variables':
                wb[sheet].cell(row=2,column=self.beg).font = openpyxl.styles.Font(color='0070C0')

            if '_variables' in self.parent.name:
                wb[sheet].cell(row=level_index,column=self.beg).alignment = openpyxl.styles.Alignment(text_rotation=45)
                if self.parent.name == 'grid_variables':
                    wb[sheet].cell(row=level_index,column=self.beg).font = openpyxl.styles.Font(color='0070C0')
                    wb[sheet].cell(row=4,column=self.beg).font = openpyxl.styles.Font(color='0070C0')
                    if self.parent.grid_set:
                        row = 5
                        for value in self.parent.grid_set[self.name]:
                            wb[sheet].cell(row=row,column=self.beg).value = value
                            row += 1
                else:
                    if self.value is not None:
                        row = 5
                        for value in self.value:
                            wb[sheet].cell(row=row,column=self.beg).value = value
                            row += 1

            if schema_node:
                # Add units
                if 'units' in schema_node:
                    wb[sheet].cell(row=4,column=self.beg).value = schema_node['units']

                # Add required
                    # TODO: Make conditional formatting (e.g. red name if not entered)

                # Add description
                if 'description' in schema_node:
                    comment = openpyxl.comments.Comment(schema_node['description'],"ASHRAE 205")
                    wb[sheet].cell(row=level_index,column=self.beg).comment = comment

            else:
                # Not found in schema
                comment = openpyxl.comments.Comment("Not found in schema.","ASHRAE 205")
                wb[sheet].cell(row=level_index,column=self.beg).comment = comment
                wb[sheet].cell(row=level_index,column=self.beg).font = openpyxl.styles.Font(color='FF0001',bold=True)

        # TODO: Something better here...a lot of repetition...
        elif self.sheet_type == SheetType.ARRAY:
            if len(self.children) > 0:
                raise Exception("Were not handling nested items in an array yet!")

            wb[sheet].cell(row=2,column=self.beg).value = self.name

            if self.value is not None:
                row = 4
                for value in self.value:
                    wb[sheet].cell(row=row,column=self.beg).value = value

                    if schema_node:
                        # Enum validation
                        if 'enum' in schema_node:
                            enumerants = f'"{",".join(schema_node["enum"])}"'
                            if len(enumerants) < 256: # Apparent limitation of written lists (TODO: https://stackoverflow.com/a/33532984/1344457)
                                dv = openpyxl.worksheet.datavalidation.DataValidation(type='list',formula1=enumerants,allow_blank=True)
                                wb[sheet].add_data_validation(dv)
                                dv.add(wb[sheet].cell(row=row,column=self.beg))

                    row += 1

            if schema_node:
                # Add units
                if 'units' in schema_node:
                    wb[sheet].cell(row=3,column=self.beg).value = schema_node['units']

                # Add required
                    # TODO: Make conditional formatting (e.g. red name if not entered)

                # Add description
                if 'description' in schema_node:
                    comment = openpyxl.comments.Comment(schema_node['description'],"ASHRAE 205")
                    wb[sheet].cell(row=2,column=self.beg).comment = comment

            else:
                # Not found in schema
                comment = openpyxl.comments.Comment("Not found in schema.","ASHRAE 205")
                wb[sheet].cell(row=2,column=self.beg).comment = comment
                wb[sheet].cell(row=2,column=self.beg).font = openpyxl.styles.Font(color='FF0001',bold=True)

        for child in self.children:
            child.write_node()

    def read_node(self):
        '''
        Translate XLSX content into nodes of a tree.
        '''
        ws = self.tree.workbook[self.child_sheet]
        end_node = False
        while not end_node:
            if self.child_sheet_type == SheetType.PERFORMANCE_MAP:
                # Everything from the perspective of parent node
                data_group = ws.cell(row=2,column=self.child_beg).value
                data_element = ws.cell(row=3,column=self.child_beg).value
                if data_group and data_group != self.name:
                    if data_group == 'grid_variables':
                        new_node = A205XLSXNode(data_group, parent=self)
                        new_node.add_grid_set({})
                        new_node.read_node()
                    elif data_group == 'lookup_variables':
                        if self.name == 'grid_variables':
                            # We hit the end of grid variables and need to conclude that node

                            # process grid set
                            grid_set = {}
                            for child in self.children:
                                grid_set[child.name] = child.value

                            self.add_grid_set(grid_set)

                            # check grid set?
                            grid_vars = process_grid_set(grid_set)

                            # reset grid variable values
                            for child in self.children:
                                child.value = grid_vars[child.name]

                            end_node = True
                        else:
                            new_node = A205XLSXNode(data_group, parent=self)
                            new_node.read_node()
                elif data_element:
                    if self.name not in ['grid_variables','lookup_variables']:
                        raise Exception(f"Invalid data group: '{self.name}'. Data groups in {self.parent.name} should be 'grid_variables' or 'lookup_variables'")
                    row = 5
                    end_of_column = False
                    value = []
                    while not end_of_column:
                        item = ws.cell(row=row,column=self.child_beg).value
                        if item is not None:
                            value.append(item)
                            row += 1
                        else:
                            end_of_column = True
                    new_node = A205XLSXNode(data_element, parent=self, value=value)
                else:
                    # End of sheet
                    end_node = True
            elif self.child_sheet_type == SheetType.ARRAY:
                # Everything from the perspective of parent node
                data_element = ws.cell(row=2,column=self.child_beg).value
                if data_element:
                    row = 4
                    end_of_column = False
                    value = []
                    while not end_of_column:
                        item = ws.cell(row=row,column=self.child_beg).value
                        if item is not None:
                            value.append(item)
                            row += 1
                        else:
                            end_of_column = True
                    new_node = A205XLSXNode(data_element, parent=self, value=value)
                else:
                    # End of sheet
                    end_node = True
            else:
                data_group = ws.cell(row=self.end,column=1).value
                data_element = ws.cell(row=self.end,column=2).value
                value = ws.cell(row=self.end,column=3).value
                if data_group:
                    lineage = data_group.split(".")
                    if len(lineage) <= self.get_num_ancestors() + 1:
                        # if lineage the same or shorter, this is not going to be a child node
                        end_node = True
                    else:
                        if value is not None:
                            new_node = A205XLSXNode(lineage[-1], parent=self, value=value)
                        else:
                            new_node = A205XLSXNode(lineage[-1], parent=self)
                        new_node.read_node()
                elif data_element:
                    level = (len(data_element) - len(data_element.lstrip(' ')))/self.white_space_multiplier
                    data_element = data_element.strip(' ')
                    generations = self.get_num_ancestors() - level
                    if generations > 0:
                        end_node = True
                    A205XLSXNode(data_element, parent=self.get_ancestor(generations), value=value)
                else:
                    # End of sheet
                    end_node = True

    def collect_content(self, content):
        '''
        Collect content from the tree and return it as a Python Dict.

        Used primarily to load contents from an XLSX sheet.
        '''
        if len(self.children) > 0:
            if self.child_sheet_type == SheetType.ARRAY:
                # Add list elements
                content[self.name] = []
                length = len(self.children[0].value)
                for i in range(length):
                    item = {}
                    for child in self.children:
                        if len(child.children) > 0:
                            raise Exception("Array sheets can only be one level deep!")
                        item[child.name] = child.value[i]
                    content[self.name].append(item)
            else:
                content[self.name] = {}
                for child in self.children:
                    child.collect_content(content[self.name])
        else:
            content[self.name] = self.value


class A205XLSXTree:

    def __init__(self):
        self.content = {}
        self.rs = ""
        self.schema = A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
        self.root_node = None
        self.sheets = []

    def load_workbook(self, file_name):
        '''
        Create tree from XLSX workbook content
        '''
        self.workbook = openpyxl.load_workbook(file_name)
        # Find Primary RS worksheet
        rs_pattern = re.compile("^RS(\\d{4})$")
        for ws in self.workbook:
            if rs_pattern.match(ws.title):
                self.rs = ws.title

        self.root_node = A205XLSXNode("ASHRAE205", tree=self)
        self.root_node.end += 1
        self.root_node.read_node()
        return self

    def create_tree_from_content(self, content, parent):
        '''
        Create tree from Python Dict content
        '''
        if type(content) == list:
            # Transpose list content
            if len(content) > 0:
                # First make nodes for each of the elements in the array
                if type(content[0]) == dict:
                    self.create_tree_from_content(content[0], parent)
                    # Override values given based on first item with empty array
                    for child in parent.children:
                        child.value = []
            for item in content:
                for child in parent.children:
                    child.value.append(item[child.name])
        else:
            for item in content:
                if type(content[item]) == dict:
                    if "performance_map" in item:
                        value = '$' + item
                    else:
                        value = None
                    new_node = A205XLSXNode(item, parent=parent, value=value)
                    if item == "grid_variables":
                        new_node.add_grid_set(self.schema.create_grid_set(content[item],new_node.lineage))
                    self.create_tree_from_content(content[item], new_node)
                elif type(content[item]) == list:
                    if len(content[item]) == 0:
                        # effectively leave blank
                        A205XLSXNode(item,parent=parent,value=content[item])
                    elif type(content[item][0]) == dict:
                        # Create new sheet for array
                        name = unique_name_with_index(item, self.sheets)
                        value = '$' + name
                        new_node = A205XLSXNode(item,parent=parent,value=value)
                        self.create_tree_from_content(content[item], new_node)
                    else:
                        A205XLSXNode(item,parent=parent,value=content[item])
                else:
                    A205XLSXNode(item,parent=parent,value=content[item])

    def load(self, content):
        '''
        Create tree from Python Dict content
        '''
        if "ASHRAE205" in content:
            if "RS_ID" in content["ASHRAE205"]:
                self.rs = content["ASHRAE205"]["RS_ID"]
            else:
                raise KeyError("Could not find 'RS_ID' key.")
        else:
            raise KeyError("Could not find 'ASHRAE205' object.")

        self.root_node = A205XLSXNode("ASHRAE205", tree=self)
        self.create_tree_from_content(content["ASHRAE205"], self.root_node)

    def create_tree_from_schema(self, node):
        '''
        Create an empty tree from the schema.

        Used largely for templating.
        '''
        schema_node = node.get_schema_node()

        # Handle nested RSs
        if 'RS' in schema_node:
            node.inner_rs = schema_node['RS']

        # typical nodes
        if 'properties' in schema_node:
            for item in schema_node['properties']:
                # Special cases
                if item == 'schema_version':
                    value = self.schema.get_schema_version()
                elif item == 'RS_ID':
                    value = node.inner_rs
                elif 'performance_map' in item:
                    value = '$' + item
                elif 'items' in schema_node['properties'][item]:
                    name = unique_name_with_index(item, self.sheets)
                    value = '$' + name
                else:
                    value = None

                self.create_tree_from_schema(A205XLSXNode(item, parent=node, value=value))

        # List nodes:
        if 'items' in schema_node:
            schema_node = self.schema.resolve(schema_node['items'],step_in=False)
            if 'properties' in schema_node:
                for item in schema_node['properties']:
                    self.create_tree_from_schema(A205XLSXNode(item, parent=node))

        # oneOf nodes
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

def template(repspec, directory):
    '''
    Generate an XLSX template based on the schema for a specific RS
    '''
    if not os.path.isdir(directory):
        os.mkdir(directory)
    tree = A205XLSXTree()
    tree.template(repspec,directory)
