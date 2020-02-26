import openpyxl
import os
import json
import re
import enum
from .tree_schema import TreeSchema
from .generic_node import A205GenericNode
from .generic_node import A205StringNode
from .generic_node import A205EnumNode
from .generic_node import A205RefNode

class A205GenericTree:

    def __init__(self):
        self.content = {}
        self.rs = ""
        schema_path = os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
        self.schema = TreeSchema(schema_path)
        self.root_node = None


    def create_tree_from_schema(self, node):
        '''
        Create a tree from the schema dict.
        '''
        schema_node = node.get_schema_node()
        if isinstance(schema_node, dict):
            for entry in schema_node:
                print('New entry ', '"'+entry+'"', 'is type', type(schema_node[entry])) # key, type(value)
                if isinstance(schema_node[entry], dict):
                    print('Creating new dict node')
                    self.create_tree_from_schema(A205GenericNode(entry, parent=node))
                elif isinstance(schema_node[entry], str):
                    print('Creating new str node')
                    self.create_tree_from_schema(A205StringNode(entry, parent=node, value=schema_node[entry]))
                elif isinstance(schema_node[entry], list):
                    print('Creating new enum node')
                    self.create_tree_from_schema(A205EnumNode(entry, parent=node, value=schema_node[entry]))
                elif "$ref" in entry:
                    print('Creating new ref node')
                    self.create_tree_from_schema(A205RefNode(entry, parent=node, value=schema_node[entry]))
    '''
            # Iterate typical tags in node (e.g. type, properties, required, additionalProperties, definitions, etc.) as keys in the schema_node dict
            # For completeness, should iterate all the possible tags, or store them in a class/struct
            if 'type' in schema_node[entry]:
                value = ''
                # type is a string describing the type of the node object: number, string, object, etc.
                if schema_node[entry]['type'] == 'object':
                    if 'properties' in schema_node[entry]:
                        # properties also a dict - what if it's empty or has one entry?
                        for it in schema_node[entry]['properties']:
                            print('Property name:', '"'+it+'"')
                            self.create_tree_from_schema(A205GenericNode(it, parent=node, value=it))
                    if 'definitions' in schema_node[entry]:
                        for d in schema_node[entry]['definitions']:
                            print('Definition name:', '"'+d+'"')
                    # Data for the object is likely in the subsequent tag "properties"
                    #self.create_tree_from_schema(A205GenericNode(schema_node[entry], parent=node, value=value))
                elif schema_node[entry]['type'] == 'string':
                    if 'enum' in schema_node[entry]:
                        # create enum variable
                        value = 'enum ' + node.name + ' {'
                        for e in schema_node[entry]['enum']:
                            value += (e + ', ')
                        value = value[:-2]
                        value += '};'
                    else:
                        #create std::string variable
                        value = 'std::string ' + node.name
                elif schema_node[entry]['type'] == 'integer':
                    # create int variable
                    value = 'int ' + node.name
                print(value)

            if 'properties' in schema_node[entry]:
                for it in schema_node[entry]['properties']:
                    print('Property name:', '"'+it+'"')
                self.create_tree_from_schema(A205GenericNode(it, parent=node, value=it))
    '''

    def template_tree(self, repspec, **kwargs):
        '''
        Generate empty tree content based on the schema for a specific RS?

        kwargs:
          any data element and value in the schema
        '''
        self.rs = repspec
        self.root_node = A205GenericNode(None, tree=self) # name=None, lineage=[]
        self.create_tree_from_schema(self.root_node)
        return self.get_content()

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

