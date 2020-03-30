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
from .generic_node import A205DefinitionsNode
from .generic_node import A205TerminalNode
from .generic_node import A205NumericNode
from .generic_node import A205BooleanNode
from .generic_node import A205VectorNode
from .generic_node import A205OneOfNode
from collections import defaultdict # we count on the ordered behavior; if using python < 3.6, try DefaultDict

class A205GenericTree:

    def __init__(self, input_path):
        self.content = {}
        self.rs = ""
        schema_path = input_path 
        self.schema = TreeSchema(schema_path)
        self.root_node = None
        self.cpp_proxy_items = defaultdict(list)
        self.cpp_enums = []
        self.top_level = True # Persistent marker for opening a cpp class
        self.last_level = 0 # Persistent storage for recursive cpp-write


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
                print('Creating new vector node')
                self.create_tree_from_schema(A205VectorNode('items', parent=node, value=schema_node['items']))
            else:
                for entry in schema_node:
                    print('New entry key', '"'+entry+'"', 'has value type', type(schema_node[entry])) # key, type(value)
                    if isinstance(schema_node[entry], dict):
                        if 'properties' in entry:
                            print('Creating new properties node (with parent', node.name, ')')
                            self.create_tree_from_schema(A205PropertiesNode(entry, parent=node, value=None))
                        elif 'definitions' in entry:
                            print('Creating new definitions node (with parent', node.name, ')')
                            self.create_tree_from_schema(A205DefinitionsNode(entry, parent=node, value=None))
                        elif 'oneOf' in entry:
                            print('Creating new oneOf node with name', node.name)
                            self.create_tree_from_schema(A205OneOfNode(entry, parent=node, value=None))
                        else:
                            print('Creating new generic dict node')
                            self.create_tree_from_schema(A205GenericNode(entry, parent=node, value=schema_node[entry]))
                    elif isinstance(schema_node[entry], str):
                        if '$ref' in entry:
                            print('Creating new ref node')
                            self.create_tree_from_schema(A205RefNode(entry, parent=node, value=schema_node[entry]))
                        elif entry == 'type': # 'type' node is the arbiter of the C++-proxy node type
                            # Should we store level here, or just get it when we re-iterate the tree?
                            if schema_node[entry] == 'number' or schema_node[entry] == 'integer':
                                print('Creating new numeric node (with parent', node.name, ')')
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
        self.root_node = A205GenericNode(None, None, tree=self) # name=None, lineage=[]
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


    def _get_enum_definitions(self, starting_node=None):
        ''' Collect definition enums from the top node down.'''
        if starting_node is None:
            starting_node = self.root_node
            self.cpp_enums.clear()
        for child in starting_node.children:
            # The enum node's grandparent is a Definitions Node (in between is the Generic Node
            # corresponding to the enum name.)
            if self._is_enum_definition(child): #isinstance(child, A205EnumNode) and isinstance(starting_node.parent, A205DefinitionsNode):
                value = child.vartype + ' ' + child.name + ';'
                self.cpp_enums.append(value)
            else:
                self._get_enum_definitions(child)
    

    def _is_enum_definition(self, node):
        '''Return True if node is an enum definition.'''
        return isinstance(node, A205EnumNode) and isinstance(node.parent.parent, A205DefinitionsNode)

    def _get_parent_property_node(self, node):
        ''' '''
        if node and isinstance(node.parent, A205PropertiesNode):
            return node.parent
        elif node.parent:
            return self._get_parent_property_node(node.parent) # Don't forget the 'return' here!
        else:
            return node # Not sure how this is going to work...@@@


    def format_cpp_2(self, starting_node=None):
        ''' '''
        if starting_node is None:
            starting_node = self.root_node
            self.top_level = True
        for child in starting_node.children:
            if not isinstance(child, A205PropertiesNode) and not self._is_enum_definition(child):
                if child.vartype and child.name:
                    value = '\t'*child.level + child.vartype + ' ' + child.name + child.suffix
                        
                    if self.last_level < child.level:
                        self.last_level = child.level

                    if self.last_level > child.level:
                        for i in range(self.last_level, child.level, -1):
                            print((i-1)*'\t' + '};')
                        self.last_level = child.level
                    print(value)
                    if self.top_level: # Should have just printed the class name line
                        for e in self.cpp_enums:
                            print('\t'*(child.level+1) + e)
                        self.top_level = False
            self.format_cpp_2(child)


    def format_cpp_3(self, starting_node=None):
        ''' '''
        self._get_enum_definitions(starting_node)
        self.format_cpp_2(starting_node)
        for i in range(self.last_level, 0, -1):
            print((i-1)*'\t' + '};')


    def format_cpp(self):
        ''' '''
        self._get_terminal_nodes_by_lineage()
        self._get_enum_definitions()
        for i in range(len(self.cpp_proxy_items.keys())):
            previous_path = list(self.cpp_proxy_items.keys())[i-1] if i > 0 else ''
            current_path = list(self.cpp_proxy_items.keys())[i]
            next_path = (list(self.cpp_proxy_items.keys())[i+1] if i < len(self.cpp_proxy_items)-1 
                                                                else '')
            
            # For each element, collect the indentation level (embeddedness) and name
            # of its unique parent struct. Only store the struct name if the element is the first
            # or only member of that struct; else store an empty string to signify the same  
            # indentation level as the previous element.

            # elif 'properties' in current_path
            item_structnames = self._property_path_to_name_list(previous_path, current_path)
            next_item_structnames = self._property_path_to_name_list(current_path, next_path)

            if len(item_structnames):
                if item_structnames[0]:
                    # If there's at least one, the first one must be the class name.
                    print ('class ' + item_structnames[0] + ' {')
                    for e in self.cpp_enums:
                        print('\t', e)
                # Open struct
                for level, s in enumerate(item_structnames[1:]):
                    # For all remaining names, indent once for each level, then 
                    # declare the struct 
                    if s:
                        print('\t'*(level+1) + 'struct ' + s + ' {')
                # Add the actual data objects
                # if len(item_structnames) >= 1 and any(item_structnames):
                for value in self.cpp_proxy_items[current_path]:
                    print('\t'*len(item_structnames), value)
                # Close struct
                if next_item_structnames.count('') <= item_structnames.count(''):
                    print('\t'*(len(item_structnames)-1) + '};')
                elif len(next_item_structnames) <= len(item_structnames):
                    print('\t'*(len(item_structnames)-1) + '};')

                if not next_path:
                    for level, s in reversed(list(enumerate(item_structnames[1:]))): # heavy but ok
                        print('\t'*(level) + '};')


    def _property_path_to_name_list(self, last_path, next_path):
        '''Convert a dot-separated string heirarchy into a list, containing empty string entries for indentation.'''
        structnames = []
        i_property = 0
        path_elements = next_path.split('.')
        previous_elements = last_path.split('.')
        while i_property >= 0:
            try:
                i_property = path_elements.index('definitions')
                # Artificially "indent" any non-enum property that's inside a definitions block
                structnames.append('')
            except Exception:
                try:
                    i_property = path_elements.index('properties')
                except:
                    i_property = -1
                    continue
            try:
                if len(previous_elements) <= i_property + 1: 
                    # If the last item had a shorter path than the current one, i.e. it was higher
                    # in the heirarchy, then the current path should be appended in full.
                    structnames.append(path_elements[i_property+1])
                else:
                    # Otherwise, for every shared heirarchy level, append empty string, and append
                    # a qualified name only for the unique level.
                    if path_elements[i_property+1] == previous_elements[i_property+1]:
                        structnames.append('')
                    else:
                        structnames.append(path_elements[i_property+1])
                path_elements = path_elements[i_property+1 : ]
                previous_elements = previous_elements[i_property+1 : ]
            except IndexError:
                i_property = -1
        return structnames


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

def view_schema(input_path):
    '''
    View the schema from which this tree is created.
    '''
    tree = A205GenericTree(input_path)
    return tree.schema.get_schema()

