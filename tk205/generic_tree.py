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
from .generic_node import A205VectorNode
from collections import defaultdict

class A205GenericTree:

    def __init__(self, input_path):
        self.content = {}
        self.rs = ""
        schema_path = input_path #os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json")
        self.schema = TreeSchema(schema_path)
        self.root_node = None
        self.cpp_proxy_items = defaultdict(list)


    def create_tree_from_schema(self, node):
        '''
        Create a tree from the schema dict.
        '''
        schema_node = node.get_schema_node()
        if isinstance(schema_node, dict):
            # Enum nodes will also have a sibling descriptor of "type" : "string" Don't double-process these nodes;
            # shortcut to enum terminal nodes before processing other types
            if 'type' in schema_node and 'enum' in schema_node:
                if isinstance(schema_node['enum'], list):
                    print('Creating new enum node')
                    self.create_tree_from_schema(A205EnumNode('enum', parent=node, value=schema_node['enum']))
            # Preemptively process array nodes too; same reason as above
            elif 'type' in schema_node and 'items' in schema_node:
                self.create_tree_from_schema(A205VectorNode('items', parent=node, value=schema_node['items']))
            else:
                for entry in schema_node:
                    print('New entry ', '"'+entry+'"', 'is type', type(schema_node[entry])) # key, type(value)
                    if isinstance(schema_node[entry], dict):
                        if 'properties' in entry or 'definitions' in entry:
                            print('Creating new definitions/properties node (with parent', node.name, ')')
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
                            if schema_node[entry] == 'number' or schema_node[entry] == 'integer':
                                print('Creating new numeric node')
                                self.create_tree_from_schema(A205NumericNode(entry, parent=node, value=schema_node[entry]))
                            elif schema_node[entry] == 'boolean':
                                print('Creating new boolean node')
                                self.create_tree_from_schema(A205BooleanNode(entry, parent=node, value=schema_node[entry]))
                            elif schema_node[entry] == 'string':
                                #prschema_node['enum']int('Creating new string node')
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


    def get_terminal_nodes(self, starting_node=None):
        if starting_node is None:
            starting_node = self.root_node
        for child in starting_node.children:
            if isinstance(child, A205TerminalNode):
                value = child.vartype + ' ' + child.name + ';'
                print(value)
            else:
                self.get_terminal_nodes(child)


    def _get_terminal_nodes_by_lineage(self, starting_node=None):
        ''' '''
        if starting_node is None:
            starting_node = self.root_node
        for child in starting_node.children:
            if isinstance(child, A205TerminalNode):
                value = child.vartype + ' ' + child.name + ';'
                # Get the lineage of the first direct 'property' node above this child
                # Using that lineage as a unique key, map this child to it as a value in a list of values
                self.cpp_proxy_items[self._get_parent_property_node(child).get_lineage_as_str()].append(value)
            else:
                self._get_terminal_nodes_by_lineage(child)


    def _get_parent_property_node(self, node):
        ''' '''
        if node and isinstance(node.parent, A205PropertiesNode):
            return node.parent
        else:
            return self._get_parent_property_node(node.parent) # Don't forget the 'return' here!


    def format_cpp(self):
        ''' '''
        print('format_cpp()')
        self._get_terminal_nodes_by_lineage()
        last_heading = ''
        for heading in self.cpp_proxy_items:
            structnames = []
            heading_elements = heading.split('.')
            print('heading', heading_elements)
            previous_elements = last_heading.split('.') # for comparison
            #print('previous', previous_elements)
            # if 'definitions' in heading, we have to do some work to move it inside a class
            if 'definitions' in heading:
                for value in self.cpp_proxy_items[heading]:
                    print('\t', value)
            # otherwise:
            property_element_index = 0
            while property_element_index >= 0:
                try:
                    property_element_index = heading_elements.index('properties')
                    if len(previous_elements) > property_element_index + 1: 
                        if heading_elements[property_element_index+1] == previous_elements[property_element_index+1]:
                            structnames.append('')
                        else:
                            structnames.append(heading_elements[property_element_index+1])
                    else:
                        structnames.append(heading_elements[property_element_index+1])
                    heading_elements = heading_elements[property_element_index+1 : ]
                    previous_elements = previous_elements[property_element_index+1 : ]
                except:
                    property_element_index = -1
            print('Parent struct names for this terminal node', structnames)
            if len(structnames):
                if structnames[0]:
                    # If there's at least one, the first one must be the class name.
                    print ('class ' + structnames[0] + ' {')
                # Open struct
                for level, s in enumerate(structnames[1:]):
                    # For all remaining names, indent once for each level, then 
                    # declare the struct 
                    if s:
                        print('\t'*(level+1) + 'struct ' + s + ' {')
                # Add the actual data objects
                for value in self.cpp_proxy_items[heading]:
                    print('\t'*len(structnames), value)
                # Close struct
                for level, s in reversed(list(enumerate(structnames[1:]))): # heavy but ok for short list
                    if s:
                        print('\t'*(level+1) + '};')

            last_heading = heading


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

