from jinja2 import Environment, FileSystemLoader
import os
import json
from functools import reduce

def get_title_and_description2(json_file, path):
    with open(os.path.join(path, json_file), 'r')as input_file:
        input_json = json.load(input_file)
        if "title" in input_json:
            title = input_json["title"]
            description = input_json["description"]
        elif "ASHRAE205" in input_json:
            title = input_json["ASHRAE205"]["RS_ID"]
            description = input_json["ASHRAE205"]["description"]
        return title, description


def get_title_and_description(file_list, path):
    title_and_description = {}
    for item in file_list:
        if isinstance(item, list):
            for subitem in os.listdir(path):
                if not subitem.startswith('.') and os.path.isdir(os.path.join(path, subitem)):
                    get_title_and_description(item, os.path.join(path, os.path.splitext(subitem)[0]))
        elif os.path.splitext(item)[-1].lower() == '.json' and os.path.isdir(os.path.join(path, item)):
            print('found')
            with open(os.path.join(path, item), 'r')as input_file:
                input_json = json.load(input_file)
                title = input_json["title"]
                description = input_json["description"]
                title_and_description[item] = [title, description]
                print(title_and_description)
    return title_and_description


def get_directory_structure(rootdir):
    """
    Recursively creates a nested dictionary that represents the folder structure of rootdir
    """
    directory_dict = {}
    contents = []
    for item in os.listdir(rootdir):
        if not item.startswith('.') and os.path.isfile(os.path.join(rootdir, item)):
            contents.append(item)
        elif not item.startswith('.') and os.path.isdir(os.path.join(rootdir, item)):
            directory_dict[item] = get_directory_structure(os.path.join(rootdir, item))
    if contents:
        return contents
    return directory_dict

def generate_page(env, template_name, file_name, destination, headline, content):
    template = env.get_template(template_name)
    html_file = os.path.join(destination, file_name)
    with open(html_file, 'w+') as f:
        f.write(template.render(
            nav = file_name,
            headline = headline,
            content = content
        )) 
    f.close()

def main():
    # Setup for Jinja
    root = os.path.dirname(os.path.abspath(__file__))
    jinja_templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(jinja_templates_dir) )
    
    # Create Destination Directory
    destination_dir = os.path.join(root, "..", "build", "html")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    schema_directory = os.path.join(root, "..", "schema-205", "schema")
    examples_directory = os.path.join(root, "..", "build", "examples")
    templates_directory = os.path.join(root, "..", "build", "templates")

    schema_dictionary = get_directory_structure(schema_directory)
    examples_dictionary = get_directory_structure(examples_directory)
    templates_dictionary = get_directory_structure(templates_directory)

    titles_and_descriptions = [] # This is a terrible solutions for this problem. these titles and descriptions are only for examples and templates, different from json.

    # Create schema.html
    schema_page_data = []
    for schema_file in sorted(schema_dictionary):
        title, description = get_title_and_description2(schema_file, schema_directory)
        schema_page_data.append([title, description, schema_file])
    generate_page(env, 'schema_template.html', 'schema.html', destination_dir, 'JSON Schema (Normative)', schema_page_data)

    # Create examples.html
    examples_page_data = []
    for example_file in sorted(examples_dictionary['json']):
        file_list = []
        title, description = get_title_and_description2(example_file, os.path.join(examples_directory, "json"))
        titles_and_descriptions.append([title, description])    # Please solve me.
        base_name = os.path.splitext(example_file)[0]
        for keys, example_types in examples_dictionary.items():
            for example in example_types:
                if base_name in example:
                    file_list.append(example)
        examples_page_data.append([title, description, file_list])
    generate_page(env, 'examples_template.html', 'examples.html', destination_dir, 'Example Files', examples_page_data)

    # Create templates.html
    templates_page_data = []
    for index, template_file in enumerate(templates_dictionary):
        templates_page_data.append([titles_and_descriptions[index][0],titles_and_descriptions[index][1], template_file])
    generate_page(env, 'schema_template.html', 'templates.html', destination_dir, 'XLSX Templates', templates_page_data)

    # Create index.html AKA about page
    generate_page(env, 'about_template.html', 'index.html', destination_dir, '', [])

    # Create toolkit205.html
    generate_page(env, 'tk205_template.html', 'tk205.html', destination_dir, '', [])


if __name__ == '__main__':
	main()
