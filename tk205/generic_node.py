import openpyxl
import os
import json
import re
import enum
from .tree_schema import TreeSchema

class A205GenericNode:

    def __init__(self, name, parent=None, tree=None, value=None):
        self.children = []  # List of children A205GenericNodes
        self.name = name  # Name of this node (i.e. key)
        self.value = value  # Value (if any) of this node
        self.vartype = None
        self.parent = parent  # Parent A205GenericNode of this node
        self.grid_set = None  # Ordered arrays of repeated grid variable values (used only for grid_variable nodes)

        if parent:
            # Inherit much information from parent
            self.lineage = self.parent.lineage + [name]  # List of parent node names (as strings)
            self.tree = self.parent.tree
            #self.inner_rs = self.parent.inner_rs

            self.parent.add_child(self)

        else:
            # Root node
            self.name = 'ROOT'
            self.lineage = []
            self.tree = tree
            #self.inner_rs = self.tree.rs

    def get_node_type(self):
        return self.__class__.__name__
        
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

    def get_ancestor(self, generation):
        if generation == 0:
            return self
        else:
            return self.parent.get_ancestor(generation - 1)

    def get_lineage_as_str(self):
        return '.'.join(self.lineage)

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

    def collect_content(self, content):
        '''
        Collect content from the owner down, and return it as a Python Dict.
        '''
        if len(self.children) > 0:
            content[self.name] = {}
            for child in self.children:
                child.collect_content(content[self.name])
        else:
            content[self.name] = self.value


class A205PropertiesNode(A205GenericNode):

    def __init__(self, name, parent=None, tree=None, value=None):
        super().__init__(name, parent, tree, value)

class A205TerminalNode(A205GenericNode):

    def __init__(self, name, parent=None, tree=None, value=None):
        super().__init__(name, parent, tree, value)

class A205StringNode(A205TerminalNode):

    def __init__(self, name, value, parent, tree=None):
        super().__init__(name, parent, tree, value)
        self.vartype = 'std::string'
        self.name = parent.name

class A205VectorNode(A205TerminalNode):

    def __init__(self, name, parent, tree=None, value=None):
        # value is None by default; the header declaration doesn't get initialized.
        super().__init__(name, parent, tree, value)
        try:
            vtype = value['type']
            stype = 'unknown' # 'object'
            if 'number' in vtype:
                stype = 'float'
            elif 'string' in vtype:
                stype = 'std::string'
            elif 'integer' in vtype:
                stype = 'int'
            self.vartype = 'std::vector<' + stype + '>'
            self.name = parent.name
        except KeyError as ke: # 'type' not in value
            self.vartype = 'std::vector<TBD>'
            self.name = parent.name


class A205NumericNode(A205TerminalNode):

    def __init__(self, name, parent, tree=None, value=None):
        # value is None by default; the header declaration doesn't get initialized.
        super().__init__(name, parent, tree, value)
        if value == 'number':
            self.vartype = 'float'
        elif value == 'integer':
            self.vartype = 'int'
        self.name = parent.name

class A205BooleanNode(A205TerminalNode):

    def __init__(self, name, value, parent, tree=None):
        super().__init__(name, parent, tree, value)
        self.vartype = 'bool'
        #self.value = 'true' if value else 'false'
        self.name = parent.name

class A205EnumNode(A205TerminalNode):

    def __init__(self, name, value, parent, tree=None):
        super().__init__(name, parent, tree, value)
        self.vartype = 'enum'
        contents = parent.name + ' {'
        for e in value:
            contents += (e + ', ')
        contents = contents[:-2]
        contents += '}'
        print(parent.parent.name)
        # Differentiate an enum variable declared in-place from an enum definition
        if parent.parent.name == 'properties':
            contents += ' _' + parent.name
        self.name = contents

class A205RefNode(A205TerminalNode):

    def __init__(self, name, value, parent, tree=None):
        super().__init__(name, parent, tree, value)
        reference = re.sub('\#', '', value)
        reference = reference.split('/') #list refering to the node lineage of a type
        self.vartype = reference[-1]
        self.name = parent.name


# self.name should probably be self.content (for terminal nodes)... but we also need a name for parent nodes...

# A terminal node of type "enum" takes precedence over one of type "string" or "number" in defining
# its parent's variable type

# Type of the node is not necessarily the "type" of the  C++ proxy I want to store; what patterns are
# available to me to convert between those?

# C++ proxy type needs a depth parameter?

# If C++ proxy objects are not stored in a tree (same or different to Node Tree) then can they
# stil be rearranged 

