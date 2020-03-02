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
            for entry in schema_node:
                print('New entry ', '"'+entry+'"', 'is type', type(schema_node[entry])) # key, type(value)
                if isinstance(schema_node[entry], dict):
                    print('Creating new dict node')
                    self.create_tree_from_schema(A205GenericNode(entry, parent=node))
                elif isinstance(schema_node[entry], str):
                    if '$ref' in entry:
                        print('Creating new ref node')
                        self.create_tree_from_schema(A205RefNode(entry, parent=node, value=schema_node[entry]))
                    else:
                        print('Creating new str node')
                        self.create_tree_from_schema(A205StringNode(entry, parent=node, value=schema_node[entry]))
                elif isinstance(schema_node[entry], (int, float)) and not isinstance(schema_node[entry], bool):
                    print('Creating new str(int) node', 'value', schema_node[entry])
                    self.create_tree_from_schema(A205StringNode(entry, parent=node, value=str(schema_node[entry])))
                elif isinstance(schema_node[entry], bool):
                    print('Creating new str(bool) node', 'value', schema_node[entry])
                    self.create_tree_from_schema(A205StringNode(entry, parent=node, value=str(schema_node[entry])))
                elif isinstance(schema_node[entry], list):
                    print('Creating new enum node')
                    self.create_tree_from_schema(A205EnumNode(entry, parent=node, value=schema_node[entry]))
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
            if 'definitions' in child.name:
                for c in child.children:
                    for node in [ch for ch in c.children if (isinstance(ch, A205EnumNode) and ch.name == 'enum')]:
                        value = 'enum ' + node.parent.name + ' {'
                        for e in node.value:
                            value += (e + ', ')
                        value = value[:-2]
                        value += '};'
                        print(value)
            else:
                self.get_definition_nodes(child)



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

