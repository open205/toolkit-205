import json
import yaml
from tk205.file_io import load, dump
import os
from collections import OrderedDict

# -------------------------------------------------------------------------------------------------
class DataElement:

    def __init__(self):
        self._Description = ''
        self._DataType    = 'String'
        self._Units       = 'h-ft2-F/Btu'
        self._Range       = '>0'
        self._Required    = True
        self._Notes       = ''


# -------------------------------------------------------------------------------------------------
class DataGroup:

    def __init__(self, name):
        self._name = name
        self._data_elements = list()

    def add_data_element(self, element_name, **kwargs):
        desc = None
        datatype = None
        required = False
        notes = None
        units = None
        minimum = None
        maximum = None

        if kwargs and 'description' in kwargs and kwargs['description'] is not None:
            desc = kwargs['description']
        if kwargs and 'data_type' in kwargs:
            if kwargs['data_type'] == 'String':
                datatype = 'string'
            elif kwargs['data_type'] == 'Numeric':
                datatype = 'number'
            elif kwargs['data_type'] == 'Integer':
                datatype = 'integer'
        if kwargs and 'required' in kwargs and kwargs['required'] is not None:
            required = kwargs['required']
        if kwargs and 'notes' in kwargs:
            notes = kwargs['notes']
        if kwargs and 'units' in kwargs:
            units = kwargs['units']
        if kwargs and 'range' in kwargs and kwargs['range'] is not None:
            ranges = kwargs['range'].split(',')
            for r in ranges:
                try:
                    if '>' in r:
                        minimum = float(r)
                    elif '<' in r:
                        maximum = float(r)
                except ValueError:
                    pass

        self._data_elements.append((element_name,
                                    desc, 
                                    datatype, 
                                    required, 
                                    notes, 
                                    units, 
                                    minimum,
                                    maximum))

    def create_dictionary_entry(self):
        entry = OrderedDict()
        elements = {'type': 'string',
                    'properties' : dict()}
        for e in self._data_elements:
            elements['properties'][e[0]] = {'description' : e[1]}
            if e[2]:
                elements['properties'][e[0]]['type'] = e[2]
            if e[4]:
                elements['properties'][e[0]]['notes'] = e[4]
            if e[5]:
                elements['properties'][e[0]]['units'] = e[5]
            if e[6]:
                elements['properties'][e[0]]['minimum'] = e[6]
            if e[7]:
                elements['properties'][e[0]]['maximum'] = e[7]
        z = list(zip(*self._data_elements))
        if any(z[3]):
            elements['required'] = [reqd_item for reqd_item in z[0] if z[3]]

        entry[self._name] = elements
        return entry


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
        self._heading = {"$schema": "http://json-schema.org/draft-07/schema#",
                   "title": "Liquid-Cooled Chiller",
                   "description": "Schema for ASHRAE 205 annex RS0001: Liquid-Cooled Chiller",
                   "definitions" : None}
        self._data_groups = list()
        self._enumerations = list()
        self._ref_declarations = list()

    def load_metaschema(self, input_file_path):
        self._contents = load(input_file_path)
        # Iterate through the dictionary, looking for fixed types
        sch = dict()
        for base_level_tag in self._contents:
            # try/except here instead of checking for 'type'?
            if ('type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['type'] == 'Enumeration'):
                sch = {**sch, **(self._process_enumeration(base_level_tag))}
            if ('type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['type'] == 'DataGroup'):
                sch = {**sch, **(self._process_datagroup(base_level_tag))}
        return sch

    def _process_enumeration(self, name_key):
        ''' Collect all Enumerators in one Enumeration block. '''
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
    sch = j.load_metaschema(os.path.join('..', 'schema-205', 'src', 'ASHRAE205.schema.yml'))
    dump(sch, 'out.json')
    # for i, e in enumerate(j._enumerations):
    #     dump(e.create_dictionary_entry(), 'out'+str(i)+'.json')



