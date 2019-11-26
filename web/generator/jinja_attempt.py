from jinja2 import Environment, FileSystemLoader
import os
from functools import reduce
from glob import glob
paths = glob('*/')

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

def generate_examples(env, content_dictionary):
    """
    Generates an 'examples.html' file from a template which contains the appropriate download buttons for the files in the
        'examples' folder of the 'assets' directory
    """
    examples_template = env.get_template('examples_template.html')

    RS0001ExampleFiles = content_dictionary['examples']['RS0001ExampleFile']
    RS0002ExampleFiles = content_dictionary['examples']['RS0002ExampleFile']
    RS0002SimpleExampleFiles = content_dictionary['examples']['RS0002SimpleExampleFile']
    RS0003ExampleFiles_continuous = content_dictionary['examples']['RS0003ExampleFile-continuous']
    RS0003ExampleFiles_discrete = content_dictionary['examples']['RS0003ExampleFile-discrete']

    with open('examples_demo.html', 'w+') as f:
        f.write(examples_template.render(
            RS0001 = RS0001ExampleFiles,
            RS0002 = RS0002ExampleFiles,
            RS0002_simple = RS0002SimpleExampleFiles,
            RS0003_continuous = RS0003ExampleFiles_continuous,
            RS0003_discrete = RS0003ExampleFiles_discrete
        )) 
    f.close()


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    
    content_directory = '../assets'
    examples_dir = os.path.join(root, content_directory)
    content_dictionary = get_directory_structure(examples_dir)

    print(content_dictionary)

    generate_examples(env, content_dictionary)


if __name__ == '__main__':
	main()

#https://medium.com/@jasonrigden/jinja2-templating-engine-tutorial-4bd31fb4aea3
#https://stackoverflow.com/questions/32254177/how-to-pass-more-than-one-parameter-in-a-jinja-loop