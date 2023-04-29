import libcst as cst
from cst_transformers import TypeAnnotationFinder, TypeAnnotationMasker
import json
from libsa4py.utils import write_file, read_file, list_files, save_json
from utils import pyright_infer
import os
from tqdm import tqdm


def extract(code):
    parsed_program = cst.parse_module(code)
    transformer = TypeAnnotationFinder()
    new_tree = cst.metadata.MetadataWrapper(parsed_program).visit(transformer)
    # print(transformer.annotated_types)
    # with open('example_types.json', 'w') as f:
    #     json.dump(transformer.annotated_types, f, indent = 4)
    return transformer.annotated_types


def mask_reveal(code, type):
    parsed_program = cst.parse_module(code)
    transformer_mask = TypeAnnotationMasker(type)
    new_tree = cst.metadata.MetadataWrapper(parsed_program).visit(transformer_mask)
    # print(new_tree.code)
    return new_tree.code
    # print(transformer.annotated_types)


if __name__ == '__main__':
    t_list = []
    files = list_files("/data/0x0FB0/pulsar")
    for file in tqdm(files):
        code = read_file(file)
        type_list = extract(code)
        for type in type_list:
            # print(type)
            code_org = code
            # print(code_org)
            code_masked = mask_reveal(code_org, type)
            write_file("temp.py", code_masked)
            predict = pyright_infer("temp.py", type["dt"], type["name"])
            if predict is not None:
                predict["label"] = type["label"]
                t_list.append(predict)
            os.remove("temp.py")
    print(t_list)
    save_json("predictions.json", t_list)
