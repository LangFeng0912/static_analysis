import libcst as cst
from cst_transformers import TypeAnnotationFinder, TypeAnnotationMasker
import json
from libsa4py.utils import write_file
from utils import pyright_infer

code = """
p: str = "hello"
def my_function(x: int, y: float) -> int:
    print("Hello, world!")
    p: int = 5
    return p + 1
"""

def extract(code):
    parsed_program = cst.parse_module(code)
    transformer = TypeAnnotationFinder()
    new_tree = cst.metadata.MetadataWrapper(parsed_program).visit(transformer)
    # print(transformer.annotated_types)
    with open('example_types.json', 'w') as f:
        json.dump(transformer.annotated_types, f, indent = 4)
    return transformer.annotated_types

def mask_reveal(code,type):
    parsed_program = cst.parse_module(code)
    transformer_mask = TypeAnnotationMasker(type)
    new_tree = cst.metadata.MetadataWrapper(parsed_program).visit(transformer_mask)
    # print(new_tree.code)
    return new_tree.code
    # print(transformer.annotated_types)

if __name__ == '__main__':
    type_list = extract(code)
    for type in type_list:
        print(type)
        code_org = code
        code_masked = mask_reveal(code_org, type)
        write_file("temp.py", code_masked)
        pyright_infer("temp.py")
