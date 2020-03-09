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
from .generic_node import A205PropertiesNode
from .generic_node import A205TerminalNode
from .generic_node import A205NumericNode
from .generic_node import A205BooleanNode

class A205GenericTree:

    def __init__(self, input_path):
        self.content = {}
        self.rs = ""
        schema_path = input_path #os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
        self.schema = TreeSchema(schema_path)
        self.root_node = None


    def create_tree_from_schema(self, node):
        '''
        Create a tree from the schema dict.
        '''
        schema_node = node.get_schema_node()
        if isinstance(schema_node, dict):
            # Enum nodes will also have a sibling descriptor of "type" : "string" Don't double-process these nodes.
            if 'type' in schema_node and 'enum' in schema_node: # Shortcut to an enum terminal node
                if isinstance(schema_node['enum'], list):
                    print('Creating new enum node')
                    self.create_tree_from_schema(A205EnumNode('enum', parent=node, value=schema_node['enum']))
            else:
                for entry in schema_node:
                    #print('New entry ', '"'+entry+'"', 'is type', type(schema_node[entry])) # key, type(value)
                    if isinstance(schema_node[entry], dict):
                        if 'properties' in entry:
                            print('Creating new properties node')
                            self.create_tree_from_schema(A205PropertiesNode(entry, parent=node))
                        else:
                            print('Creating new dict node')
                            self.create_tree_from_schema(A205GenericNode(entry, parent=node))
                    elif isinstance(schema_node[entry], str):
                        if '$ref' in entry:
                            print('Creating new ref node')
                            self.create_tree_from_schema(A205RefNode(entry, parent=node, value=schema_node[entry]))
                        elif entry == 'type': # 'type' node is the arbiter of the C++-proxy node type
                            print('Creating new str node with JSON type', schema_node[entry])
                            # Should we store level here, or just get it when we re-iterate the tree?
                            if schema_node[entry] == 'number':
                                print('Creating new numeric node')
                                self.create_tree_from_schema(A205NumericNode(entry, parent=node, value=schema_node[entry]))
                            elif schema_node[entry] == 'boolean':
                                print('Creating new boolean node')
                                self.create_tree_from_schema(A205BooleanNode(entry, parent=node, value=schema_node[entry]))
                            elif schema_node[entry] == 'string':
                                print('Creating new string node')
                                self.create_tree_from_schema(A205StringNode(entry, parent=node, value=schema_node[entry]))

    def template_tree(self):
        '''
        Generate empty tree content based on the schema for a specific RS?

        kwargs:
          any data element and value in the schema
        '''
        #self.rs = repspec
        self.root_node = A205GenericNode(None, tree=self) # name=None, lineage=[]
        self.create_tree_from_schema(self.root_node)
        return self

    def get_content(self):
        '''
        returns tree content
        '''
        content = {}
        self.root_node.collect_content(content)
        return content

    def get_definition_nodes(self, starting_node=None):
        if starting_node is None:
            starting_node = self.root_node
        for child in starting_node.children:
            if isinstance(child, A205EnumNode):
                value = child.vartype + ' ' + starting_node.name + ' {'
                for e in child.value:
                    value += (e + ', ')
                value = value[:-2]
                value += '};'
                print(value)
            # if 'definitions' in child.name:
            #     for kid in child.children:
            #         # Differentiate 'enum' from 'enum_text', both of which are valid nodes
            #         for grandkid in [ch for ch in kid.children if (isinstance(ch, A205EnumNode) and ch.name == 'enum')]:
            #             value = grandkid.vartype + ' ' + kid.name + ' {'
            #             for e in grandkid.value:
            #                 value += (e + ', ')
            #             value = value[:-2]
            #             value += '};'
            #             print(value)
            #         # For each property node under a named definition...
            #         for grandkid in [ch for ch in kid.children if (isinstance(ch, A205PropertiesNode))]:
            #             for k in grandkid.children:
            #                 self.get_base_data_nodes(k)
            else:
                self.get_definition_nodes(child)

    def get_terminal_nodes(self, starting_node=None):
        if starting_node is None:
            starting_node = self.root_node
        for child in starting_node.children:
            if isinstance(child, A205TerminalNode):
                value = child.vartype + ' ' + child.name + ';'
                print(value)
            else:
                self.get_terminal_nodes(child)
               


def iterdict(d, level=0):
    for key in d:
        if isinstance(d[key], dict):
            print('Level', level, '  '*level, key, ':', '[dict]')
            iterdict(d[key], level+1)
        else:
           print('Level', level, '  '*level, key, ':', d[key])

def build_tree(input_path):
    '''
    Generate a tree based on the schema for a specific RS
    '''
    tree = A205GenericTree(input_path)
    return tree.template_tree()

def view_schema():
    '''
    View the schema from which this tree is created.
    '''
    tree = A205GenericTree()
    return tree.schema.get_schema()

