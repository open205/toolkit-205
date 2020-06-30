import json
import yaml
from tk205.file_io import load, dump
import os
from collections import OrderedDict
import re
import enum
import sys

# -------------------------------------------------------------------------------------------------
class DataGroup:

    def __init__(self, name, ref_list=None):
        self._name = name
        self._refs = ref_list


    def add_data_group(self, group_name, group_subdict):
        elements = {'type': 'object',
                    'properties' : dict()}
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
            if required:
                elements['required'] = required
            elements['additionalProperties'] = False

        return {group_name : elements}


    def _create_type_entry(self, parent_dict, target_dict):
        try:
            # If the type is an array, extract the surrounding [] first (using non-greedy qualifier "?")
            m = re.findall(r'\[(.*?)\]', parent_dict['Data Type'])
            if m:
                target_dict['type'] = 'array'
                target_dict['items'] = dict()
                k, v = self._get_simple_type(m[0])
                target_dict['items'][k] = v
                if 'Range' in parent_dict:
                    self._get_simple_minmax(parent_dict['Range'], target_dict['items'])
                if len(m) > 1:
                    target_dict['minItems'] = int(m[1])
                    target_dict['maxItems'] = int(m[1])
                else:
                    target_dict['minItems'] = 1
            else:
                k, v = self._get_simple_type(parent_dict['Data Type'])
                target_dict[k] = v
                self._get_simple_minmax(parent_dict['Range'], target_dict)
        except KeyError as ke:
            #print('KeyError; no key exists called', ke)
            pass


    def _get_simple_type(self, type_str):
        enum_or_def = r'(\{|\<)(.*)(\}|\>)'

        m = re.match(enum_or_def, type_str)
        if m:
            internal_type = m.group(2)
            for key in self._refs:
                if internal_type in self._refs[key]:
                    internal_type = key + '.schema.json#/definitions/' + internal_type
            return ('$ref', internal_type)

        if type_str == 'String':
            return ('type', 'string')
        elif type_str == 'Numeric':
            return ('type', 'number')
        elif type_str == 'Integer':
            return ('type', 'integer')
        elif type_str == 'Boolean':
            return ('type', 'boolean')
        else:
            # Validation error
            print('Type not processed:', type_str)
            return (None, None)


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

    def __init__(self, name, description=None):
        self._name = name
        self._description = description
        self._enumerants = list() # list of tuple:[value, description, display_text, notes]
        self.entry = dict()
        self.entry[self._name] = dict()
        self.entry[self._name]['description'] = self._description

    def add_enumerator(self, value, description=None, display_text=None, notes=None):
        self._enumerants.append((value, description, display_text, notes))

    def create_dictionary_entry(self):
        z = list(zip(*self._enumerants))
        enums = {'type': 'string', 
                 'enum' : z[0]}
        if any(z[2]):
            enums['enum_text'] = z[2]
        if any(z[1]):
            enums['descriptions'] = z[1]
        if any(z[3]):
            enums['notes'] = z[3]
        self.entry[self._name] = {**self.entry[self._name], **enums}
        return self.entry


# -------------------------------------------------------------------------------------------------
class JSON_translator:
    def __init__(self):
        self._schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                        'title': None,
                        'description': None,
                        'definitions' : dict()}
        self._references = dict()
        self._datatypes = list()


    def load_metaschema(self, input_rs):
        ''' '''
        self._input_rs = input_rs
        input_file_path = os.path.join('..', 'schema-205', 'src', input_rs + '.schema.yaml')
        self._contents = load(input_file_path)
        sch = dict()
        # Iterate through the dictionary, looking for known types
        for base_level_tag in self._contents:
            if 'Object Type' in self._contents[base_level_tag]:
                obj_type = self._contents[base_level_tag]['Object Type']
                if obj_type == 'Meta':
                    self._load_meta_info(self._contents[base_level_tag])
                if obj_type == 'Data Type' and 'Is Regex' in self._contents[base_level_tag]:
                    sch = {**sch, **({base_level_tag : {"type":"string", "regex":True}})}
                elif obj_type == 'Data Type':
                    pass
                if obj_type == 'Enumeration':
                    sch = {**sch, **(self._process_enumeration(base_level_tag))}
                if obj_type == 'Data Group':
                    dg = DataGroup(base_level_tag, self._references)
                    sch = {**sch, **(dg.add_data_group(base_level_tag, 
                                     self._contents[base_level_tag]['Data Elements']))}
                if obj_type == 'Performance Map':
                    dg = DataGroup(base_level_tag, self._references)
                    sch = {**sch, **(dg.add_data_group(base_level_tag, 
                                     self._contents[base_level_tag]['Data Elements']))}
                if obj_type == 'Grid Variables':
                    dg = DataGroup(base_level_tag, self._references)
                    sch = {**sch, **(dg.add_data_group(base_level_tag, 
                                     self._contents[base_level_tag]['Data Elements']))}
                if obj_type == 'Lookup Variables':
                    dg = DataGroup(base_level_tag, self._references)
                    sch = {**sch, **(dg.add_data_group(base_level_tag, 
                                     self._contents[base_level_tag]['Data Elements']))}
        self._schema['definitions'] = sch
        return self._schema


    def _load_meta_info(self, schema_section):
        self._schema['title'] = schema_section['Title']
        self._schema['description'] = schema_section['Description']
        # Create a dictionary of available external objects for reference
        if 'References' in schema_section:
            refs = schema_section['References']
            refs.append(self._input_rs)
            for ref_file in schema_section['References']:
                ext_dict = load(os.path.join('..', 'schema-205', 'src', ref_file + '.schema.yaml'))
                external_objects = list()
                for base_item in ext_dict:
                    external_objects.append(base_item)
                self._references[ref_file] = external_objects


    def _process_enumeration(self, name_key):
        ''' Collect all Enumerators in an Enumeration block. '''
        enums = self._contents[name_key]['Enumerators']
        description = self._contents[name_key].get('Description')
        definition = Enumeration(name_key, description)
        for key in enums:
            try:
                descr = enums[key]['Description']  if 'Description'  in enums[key] else None
                displ = (enums[key]['Display Text'] if 'Display Text' in enums[key] else
                        (descr if descr else None))
                notes = enums[key]['Notes']        if 'Notes'        in enums[key] else None
                definition.add_enumerator(key, descr, displ, notes)
            except TypeError: # key's value is None
                definition.add_enumerator(key)
        return definition.create_dictionary_entry()


# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    j = JSON_translator()
    sch = j.load_metaschema('ASHRAE205')
    dump(sch, 'out.json')



