import libcst as cst
from cst_transformers import TypeAnnotationFinder

code = """
def my_function(x: int, y: float) -> int:
    p: int = 5
    print("Hello, world!")
    return 1
"""

def extract(code):
    parsed_program = cst.parse_module(code)
    transformer = TypeAnnotationFinder()
    new_tree = parsed_program.visit(transformer)
    print(transformer.annotated_types)



if __name__ == '__main__':
    extract(code)