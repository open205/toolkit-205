import json
import yaml
from tk205.file_io import load, dump
import os
from collections import OrderedDict
import re
import enum

# -------------------------------------------------------------------------------------------------
class DataGroup:

    class Index(enum.IntEnum):
        name = 0
        descriptor = 1
        datatype = 2
        required = 3
        notes = 4
        units = 5
        minimum = 6
        maximum = 7

    def __init__(self, name):
        self._name = name
        self._data_elements = list()


    def add_data_group(self, group_name, group_subdict):
        elements = {'type': 'object',
                    'properties' : dict(),
                    'additionalProperties' : False}
        required = list()
        for e in group_subdict:
            element = group_subdict[e]
            if 'Description' in element:
                elements['properties'][e] = {'description' : element['Description']}
            if 'Data Type' in element:
                self._create_type_entry(group_subdict[e], elements['properties'][e])
            if 'Units' in element:
                elements['properties'][e]['units'] = element['Units']
            if 'Notes' in element:
                elements['properties'][e]['notes'] = element['Notes']
            if 'Required' in element:
                required.append(e)
            elements['required'] = required

        return {group_name : elements}


    def _create_type_entry(self, parent_dict, target_dict):
        try:
            # If the type is an array, extract the surrounding [] first (using non-greedy qualifier "?")
            m = re.match(r'\[(.*?)\]', parent_dict['Data Type'])
            if m:
                target_dict['type'] = 'array'
                target_dict['items'] = dict()
                target_dict['items']['type'] = self._get_simple_type(m.group(1))
                self._get_simple_minmax(parent_dict['Range'], target_dict['items'])
                if len(m.groups()) > 1:
                    target_dict['minItems'] = int(m.group(2))
                    target_dict['maxItems'] = int(m.group(2))
                else:
                    target_dict['minItems'] = 1
            else:
                target_dict['type'] = self._get_simple_type(parent_dict['Data Type'])
                self._get_simple_minmax(parent_dict['Range'], target_dict)
        except KeyError:
            # some good error msg for two keys, esp. Range
            pass


    def _get_simple_type(self, type_str):
        m = re.match(r'\{(.*)\}', type_str)
        if m: # Enum type
            internal_type = m.group(1)
            return internal_type
        if type_str == 'String':
            return 'string'
        elif type_str == 'Numeric':
            return 'number'
        elif type_str == 'Integer':
            return 'integer'
        elif type_str == 'Boolean':
            return 'boolean'
        else:
            # Validation error
            return None


    def _get_simple_minmax(self, range_str, target_dict):
        if range_str is not None:
            ranges = range_str.split(',')
            minimum=None
            maximum=None
            for r in ranges:
                try:
                    numerical_value = re.findall(r'\d+', r)[0]
                    if '>' in r:
                        minimum = (float(numerical_value) if target_dict['type'] == 'number' else int(numerical_value))
                        mn = 'exclusiveMinimum' if '=' not in r else 'minimum'
                        target_dict[mn] = minimum
                    elif '<' in r:
                        maximum = (float(numerical_value) if target_dict['type'] == 'number' else int(numerical_value))
                        mx = 'exclusiveMaximum' if '=' not in r else 'maximum'
                        target_dict[mx] = maximum
                except ValueError:
                    pass


# -------------------------------------------------------------------------------------------------
class Enumeration:

    def __init__(self, name):
        self.name = name
        self._enumerants = list() # list of tuple:[value, description, display_text, notes]

    def add_enumerator(self, value, description=None, display_text=None, notes=None):
        self._enumerants.append((value, description, display_text, notes))

    def create_dictionary_entry(self):
        entry = OrderedDict()
        z = list(zip(*self._enumerants))
        enums = {'type': 'string', 
                 'enum' : z[0]}
        if any(z[1]):
            enums['descriptions'] = z[1]
        if any(z[2]):
            enums['enum_text'] = z[2]
        if any(z[3]):
            enums['notes'] = z[3]
        entry[self.name] = enums
        return entry


# -------------------------------------------------------------------------------------------------
class JSON_translator:
    def __init__(self):
        self._schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                   'title': 'Liquid-Cooled Chiller',
                   'description': 'Schema for ASHRAE 205 annex RS0001: Liquid-Cooled Chiller',
                   'definitions' : dict()}

    def load_metaschema(self, input_file_path):
        ''' '''
        self._contents = load(input_file_path)
        # Iterate through the dictionary, looking for fixed types
        sch = self._schema['definitions']
        for base_level_tag in self._contents:
            # try/except here instead of checking for 'type'?
            if ('Object Type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['Object Type'] == 'Enumeration'):
                sch = {**sch, **(self._process_enumeration(base_level_tag))}
            if ('Object Type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['Object Type'] == 'Data Group'):
                #sch = {**sch, **(self._process_datagroup(base_level_tag))}
                dg = DataGroup(base_level_tag)
                sch = {**sch, **(dg.add_data_group(base_level_tag, self._contents[base_level_tag]['Data Elements']))}
        self._schema['definitions'] = sch
        return self._schema

    def _process_enumeration(self, name_key):
        ''' Collect all Enumerators in an Enumeration block. '''
        definition = Enumeration(name_key)
        enums = self._contents[name_key]['Enumerators']
        for key in enums:
            try: #if enums[key]:
                descr = enums[key]['Description']  if 'Description'  in enums[key] else None
                displ = enums[key]['Display Text'] if 'Display Text' in enums[key] else None
                notes = enums[key]['Notes']        if 'Notes'        in enums[key] else None
                definition.add_enumerator(key, descr, displ, notes)
            except TypeError: # key's value is None
                definition.add_enumerator(key)
        return definition.create_dictionary_entry()

    def _process_datagroup(self, name_key):
        ''' Collect all Data Elements in a DataGroup block. '''
        datagroup = DataGroup(name_key)
        elements = self._contents[name_key]['Data Elements']
        for key in elements: # keys are actual property names
            try:
                datagroup.add_data_element(key, 
                    description=elements[key]['Description'] if 'Description' in elements[key] else None,
                    data_type=elements[key]['Data Type'] if 'Data Type' in elements[key] else None,
                    notes=elements[key]['Notes'] if 'Notes' in elements[key] else None,
                    required=elements[key]['Required'] if 'Required' in elements[key] else None,
                    units=elements[key]['Units'] if 'Units' in elements[key] else None,
                    range=elements[key]['Range'] if 'Range' in elements[key] else None)
            except TypeError:
                pass 
        return datagroup.create_dictionary_entry()


# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    j = JSON_translator()
    sch = j.load_metaschema(os.path.join('..', 'schema-205', 'src', 'RS0001.schema.yml'))
    dump(sch, 'out.json')



