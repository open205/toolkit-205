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

    def __init__(self):
        self._data_elements = list()


# -------------------------------------------------------------------------------------------------
class Enumeration:

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.enumerants = list() # list of tuple:[value, description, display_text, notes]

    def add_enumerator(self, value, description=None, display_text=None, notes=None):
        self.enumerants.append((value, description, display_text, notes))

    def create_dictionary_entry(self):
        entry = OrderedDict()
        z = list(zip(*self.enumerants))
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
        for base_level_tag in self._contents:
            # try/except here instead of checking for 'type'?
            if ('type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['type'] == 'Enumeration'):
                self._process_enumerations(base_level_tag, 
                                           self._contents[base_level_tag]['Enumerators'])
            if ('type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['type'] == 'DataGroup'):
                self._process_datagroup(base_level_tag, 
                                           self._contents[base_level_tag]['Data Elements'])

    def _process_enumerations(self, name_key, subdict):
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
        self._enumerations.append(definition)

    def _process_datagroup(self, name_key, subdict):
        pass

# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    j = JSON_translator()
    j.load_metaschema(os.path.join('..', 'schema-205', 'src', 'ASHRAE205.schema.yml'))
    for i, e in enumerate(j._enumerations):
        dump(e.create_dictionary_entry(), 'out'+str(i)+'.json')



