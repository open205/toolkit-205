import git
import os
import json
import datetime
from collections import OrderedDict
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader
import markdown
import tk205
from tk205.file_io import set_dir

root_dir = os.path.dirname(os.path.abspath(__file__))

def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.InvalidGitRepositoryError:
        return False

def get_title_and_description(json_file, path):
    """
    Open an ASHRAE205 json schema or example file and return the title and description.
    """
    with open(os.path.join(path, json_file), 'r')as input_file:
        input_json = json.load(input_file)
        if "title" in input_json:
            title = input_json["title"]
            description = input_json["description"]
        else:
            title = input_json["RS_ID"]
            description = input_json["description"]
        return title, description


def get_directory_structure(rootdir):
    """
    Recursively creates a nested dictionary that represents the folder structure of rootdir.
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


def generate_page(env, template_name, file_name, destination, headline, markdown=None, content=None):
    """
    Create a specific html page of the open205.github.io website from a Jinja2 template.
    """
    template = env.get_template(template_name)
    html_file = os.path.join(destination, file_name)
    with open(html_file, 'w+') as f:
        f.write(template.render(
            nav = file_name,
            headline = headline,
            markdown = markdown,
            content = content,
            timestamp = datetime.datetime.now().replace(tzinfo = datetime.timezone.utc)
        ))
    f.close()


def create_files(web_dir):
    """
    Create or replace the example and template files inside of open205.github.io
    """
    assets_dir = set_dir(os.path.join(web_dir, 'assets'))

    examples_dir = set_dir(os.path.join(assets_dir, 'examples'))

    json_dir = set_dir(os.path.join(examples_dir, 'json'))
    cbor_dir = set_dir(os.path.join(examples_dir, 'cbor'))
    xlsx_dir = set_dir(os.path.join(examples_dir, 'xlsx'))
    yaml_dir = set_dir(os.path.join(examples_dir, 'yaml'))

    templates_dir = set_dir(os.path.join(assets_dir, 'templates'))

    schema_dir = set_dir(os.path.join(assets_dir, 'schema'))

    for rs_folder in os.listdir('schema-205/examples'):
        tranlate_dir = os.path.join('schema-205/examples', rs_folder)
        tk205.translate_directory_recursive(tranlate_dir, json_dir, ".json")
        tk205.translate_directory_recursive(tranlate_dir, cbor_dir, ".cbor")
        tk205.translate_directory_recursive(tranlate_dir, xlsx_dir, ".xlsx")
        tk205.translate_directory_recursive(tranlate_dir, yaml_dir, ".yaml")

    copy_tree('schema-205/schema', schema_dir)

    # xlsx_template_creation
    tk205.file_io.clear_directory(templates_dir)
    template_content = tk205.load(os.path.join(root_dir, "..", "config", "templates.json"))
    for RS, templates in template_content.items():
        for template in templates:
            file_name_components = [RS]
            if template["file-name-suffix"]:
                file_name_components.append(template["file-name-suffix"])
            file_name_components.append("template.a205.xlsx")
            file_name = '-'.join(file_name_components)
            tk205.template(RS,os.path.join(templates_dir,file_name), **template["keywords"])


def clone():
    """
    Clone open205.github.io website repository into the build directory.
    """
    build_dir = set_dir(os.path.join(root_dir, '..', 'build'))
    web_dir = os.path.join(build_dir, 'web')
    if os.path.isdir(web_dir) and is_git_repo(web_dir):
        pass
    elif os.path.isdir(web_dir) and not is_git_repo(web_dir):
        print("Working folder found. Continuing without git repository...")
    else:
        try:
            git.Repo.clone_from("https://github.com/open205/open205.github.io.git", web_dir, branch='master')
        except git.GitError as e:
            print(f"GitPython Error: {e}")
            print("Continuing without git repository...")
            set_dir(web_dir)
    return web_dir


def generate(web_dir):
    """
    Generate all content for the open205.github.io repository
    """
    # Setup for Jinja2
    jinja_templates_dir = os.path.join(root_dir, 'templates')
    env = Environment( loader = FileSystemLoader(jinja_templates_dir) )

    schema_directory = os.path.join(root_dir, "..", "schema-205", "schema")
    examples_directory = os.path.join(web_dir, "assets", "examples")
    templates_directory = os.path.join(web_dir, "assets", "templates")

    schema_dictionary = get_directory_structure(schema_directory)
    examples_dictionary = get_directory_structure(examples_directory)
    templates_dictionary = get_directory_structure(templates_directory)

    schema_title_description = [] # This is stored during the schema page data generation to be saved and used in the templates page

    # Create schema.html
    with open(os.path.join(root_dir, 'markdown-content', 'schema.md')) as md_file:
        md_content = md_file.read()
    markdown_html = markdown.markdown(md_content)

    schema_page_data = OrderedDict()
    for schema_file in sorted(schema_dictionary):
        schema_file_name = schema_file.split('.')
        RS = schema_file_name[0]
        title, description = get_title_and_description(schema_file, schema_directory)
        title_description_tupel = (title, description)
        if RS != "ASHRAE205": # if file is the 205 schema itself, use only the schema title
            title = RS + ": " + title
        schema_title_description.append(title_description_tupel)
        schema_page_data[RS] = {'title': title, 'description': description, 'schema_file': schema_file}

    generate_page(env, 'schema_template.html', 'schema.html', web_dir, 'JSON Schema (Normative)', markdown=markdown_html, content=schema_page_data)

    # Create examples.html
    with open(os.path.join(root_dir, 'markdown-content', 'examples.md')) as md_file:
        md_content = md_file.read()
    markdown_html = markdown.markdown(md_content)

    examples_page_data = OrderedDict()
    #   The purpose of the below loop is to loop through and initialize the `examples_page_data[title_and_description]` arrays outside of the following loop
    #   Attempting to do this inside a single loop results in the array being reinitialized, and thus wiping out data.
    for i, example_file in enumerate(sorted(examples_dictionary['json'])):
        RS, description = get_title_and_description(example_file, os.path.join(examples_directory, "json"))
        title_and_description = ""
        for title, schema_description in schema_title_description:
            if RS in schema_description:
                title_and_description = RS + ": " + title
                examples_page_data[title_and_description] = []
    for i, example_file in enumerate(sorted(examples_dictionary['json'])):
        file_list = []
        RS, description = get_title_and_description(example_file, os.path.join(examples_directory, "json"))
        title_and_description = ""
        for title, schema_description in schema_title_description:
            if RS in schema_description:
                title_and_description = RS + ": " + title
        base_name = os.path.splitext(example_file)[0]
        for key in examples_dictionary:
            for example in examples_dictionary[key]:
                if base_name in example:
                    file_list.append(example)
        examples_page_data[title_and_description].append({'title': RS, 'description': description, 'file_list': file_list})

    generate_page(env, 'examples_template.html', 'examples.html', web_dir, 'Example Files', markdown=markdown_html, content=examples_page_data)

    # Create templates.html
    with open(os.path.join(root_dir, 'markdown-content', 'templates.md')) as md_file:
        md_content = md_file.read()
    markdown_html = markdown.markdown(md_content)

    template_content = tk205.load(os.path.join(root_dir, "..", "config", "templates.json"))
    templates_page_data = OrderedDict()
    templates_dictionary.sort()
    j=0
    for i, (RS, content) in enumerate(template_content.items()):
        title, description = schema_title_description[i+1]
        title_and_description = RS + ": " + title
        templates_page_data[title_and_description] = []
        for item in content:
            templates_page_data[title_and_description].append({'title':RS, 'description':item['description'], 'template_file':templates_dictionary[j]})
            j += 1

    generate_page(env, 'templates_template.html', 'templates.html', web_dir, 'XLSX Templates', markdown=markdown_html, content=templates_page_data)

    # Create index.html AKA about page
    with open(os.path.join(root_dir, 'markdown-content', 'about.md')) as md_file:
        md_content = md_file.read()
    markdown_html = markdown.markdown(md_content)

    generate_page(env, 'about_template.html', 'index.html', web_dir, '', markdown=markdown_html)

    # Create toolkit205.html
    with open(os.path.join(root_dir, 'markdown-content', 'tk205.md')) as md_file:
        md_content = md_file.read()
    markdown_html = markdown.markdown(md_content)

    generate_page(env, 'tk205_template.html', 'tk205.html', web_dir, '', markdown=markdown_html)


def main():
    web_dir = clone()
    create_files(web_dir)
    generate(web_dir)


if __name__ == '__main__':
	main()
