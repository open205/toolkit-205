from jinja2 import Environment, FileSystemLoader
import os
import json
from collections import OrderedDict 

def get_title_and_description(json_file, path):
    with open(os.path.join(path, json_file), 'r')as input_file:
        input_json = json.load(input_file)
        if "title" in input_json:
            title = input_json["title"]
            description = input_json["description"]
        elif "ASHRAE205" in input_json:
            title = input_json["ASHRAE205"]["RS_ID"]
            description = input_json["ASHRAE205"]["description"]
        return title, description

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

def generate():
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

    titles_and_descriptions = []

    # Create schema.html
    schema_page_data = OrderedDict() 
    for schema_file in sorted(schema_dictionary):
        title, description = get_title_and_description(schema_file, schema_directory)
        schema_page_data[title] = {'title':title, 'description':description, 'schema_file':schema_file}
    generate_page(env, 'schema_template.html', 'schema.html', destination_dir, 'JSON Schema (Normative)', schema_page_data)

    # Create examples.html
    examples_page_data = OrderedDict()
    for example_file in sorted(examples_dictionary['json']):
        file_list = []
        title, description = get_title_and_description(example_file, os.path.join(examples_directory, "json"))
        titles_and_descriptions.append({'title':title, 'description':description})
        base_name = os.path.splitext(example_file)[0]
        for keys, example_types in examples_dictionary.items():
            for example in example_types:
                if base_name in example:
                    file_list.append(example)
        examples_page_data[example_file]={'title':title, 'description':description, 'file_list':file_list}
    generate_page(env, 'examples_template.html', 'examples.html', destination_dir, 'Example Files', examples_page_data)

    # Create templates.html
    templates_page_data = OrderedDict()
    for index, template_file in enumerate(templates_dictionary):
        templates_page_data[template_file] = {'title':titles_and_descriptions[index]['title'], 'description':titles_and_descriptions[index]['description'], 'template_file':template_file}
    generate_page(env, 'templates_template.html', 'templates.html', destination_dir, 'XLSX Templates', templates_page_data)

    # Create index.html AKA about page
    generate_page(env, 'about_template.html', 'index.html', destination_dir, '', [])

    # Create toolkit205.html
    generate_page(env, 'tk205_template.html', 'tk205.html', destination_dir, '', [])

def main():
    generate()

if __name__ == '__main__':
	main()
