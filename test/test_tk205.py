import tk205
import os

def test_validate_examples():
    example_dir = 'examples/json'
    for example in os.listdir(example_dir):
        print(example)
        tk205.validate(os.path.join(example_dir,example))