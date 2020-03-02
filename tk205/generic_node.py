import openpyxl
import os
import json
import re
import enum
from .tree_schema import TreeSchema
from .util import process_grid_set, unique_name_with_index

class A205GenericNode:

    def __init__(self, name, parent=None, tree=None, value=None):
        self.children = []  # List of children A205GenericNodes
        self.name = name  # Name of this node (i.e. key)
        self.value = value  # Value (if any) of this node
        self.parent = parent  # Parent A205GenericNode of this node
        self.grid_set = None  # Ordered arrays of repeated grid variable values (used only for grid_variable nodes)

        if parent:
            # Inherit much information from parent
            self.lineage = self.parent.lineage + [name]  # List of parent node names (as strings)
            self.tree = self.parent.tree
            self.inner_rs = self.parent.inner_rs

            self.parent.add_child(self)

        else:
            # Root node
            self.name = 'ROOT'
            self.lineage = []
            self.tree = tree
            self.inner_rs = self.tree.rs

    def add_child(self, node):
        '''
        Add a child node to this node.
        '''
        self.children.append(node)

    def get_ancestor(self,generation):
        if generation == 0:
            return self
        else:
            return self.parent.get_ancestor(generation - 1)

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


class A205StringNode(A205GenericNode):

    def __init__(self, name, value, parent=None, tree=None):
        super().__init__(name, parent, tree)
        self.value = value #string

class A205EnumNode(A205GenericNode):

    def __init__(self, name, value, parent=None, tree=None):
        super().__init__(name, parent, tree)
        self.value = value #string list

class A205RefNode(A205GenericNode):

    def __init__(self, name, value, parent=None, tree=None):
        super().__init__(name, parent, tree)
        print('A205RefNode parent', parent.name)
        self.value = value #string refering to the node lineage of a type
        print('self.value', self.value)