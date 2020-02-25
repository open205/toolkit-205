import openpyxl
import os
import json
import re
import enum
from .tree_schema import TreeSchema
from .generic_node import A205GenericNode

class A205GenericTree:

    def __init__(self):
        self.content = {}
        self.rs = ""
        schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
        self.schema = TreeSchema(schema_path)
        self.root_node = None


    def create_tree_from_schema(self, node):
        '''
        Create an empty tree from the schema.
        '''
        schema_node = node.get_schema_node()
        print('create_tree_from_schema: schema_node=', schema_node)

        # Handle nested RSs
        # if 'RS' in schema_node:
        #     node.inner_rs = schema_node['RS']

        # Iterate typical tags in node (e.g. type, properties, required, additionalProperties, definitions, etc.) as keys in the schema_node dict
        # For completeness, should iterate all the possible tags, or store them in a class/struct

        if 'type' in schema_node:
            value = ''
            # type is a string describing the type of the node object: number, string, object, etc.
            if schema_node['type'] == 'object':
                if 'properties' in schema_node:
                    # properties also a dict - what if it's empty or has one item?
                    for item in schema_node['properties']:
                        print('Property name:', '"'+item+'"')
                        self.create_tree_from_schema(A205GenericNode(item, parent=node, value=item))
                if 'definitions' in schema_node:
                    for d in schema_node['definitions']:
                        print('Definition name:', '"'+d+'"')
                # Data for the object is likely in the subsequent tag "properties"
                #self.create_tree_from_schema(A205GenericNode(item, parent=node, value=value))
            elif schema_node['type'] == 'string':
                if 'enum' in schema_node:
                    # create enum variable
                    value = 'enum ' + node.name + ' {'
                    for e in schema_node['enum']:
                        value += (e + ', ')
                    value = value[:-2]
                    value += '};'
                else:
                    #create std::string variable
                    value = 'std::string ' + node.name
            elif schema_node['type'] == 'integer':
                # create int variable
                value = 'int ' + node.name
            print(value)

        # if 'properties' in schema_node:
        #     # properties also a dict - what if it's empty or has one item?
        #     for item in schema_node['properties']:
        #         print('Property name:', '"'+item+'"')
        #     self.create_tree_from_schema(A205GenericNode(item, parent=node, value=item))

    def template_tree(self, repspec, **kwargs):
        '''
        Generate empty tree content based on the schema for a specific RS?

        kwargs:
          any data element and value in the schema
        '''
        self.rs = repspec
        self.root_node = A205GenericNode(None, tree=self)
        self.create_tree_from_schema(self.root_node)

    def get_content(self):
        '''
        returns tree content
        '''
        content = {}
        self.root_node.collect_content(content)
        return content


def build_tree(repspec, output_path, **kwargs):
    '''
    Generate a tree based on the schema for a specific RS
    '''
    tree = A205GenericTree()
    return tree.template_tree(repspec, **kwargs)

def view_schema():
    '''
    View the schema from which this tree is created.
    '''
    tree = A205GenericTree()
    return tree.schema.get_schema()

