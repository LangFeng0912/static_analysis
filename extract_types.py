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
    files = list_files("/data/acoustid/acoustid-server")
    for file in tqdm(files):
        # print(file)
        code = read_file(file)
        type_list = extract(code)
        for type_info in type_list:
            # print(type)
            if type_info["label"] in ["None", "typing.Any"]:
                continue
            label = type_info["label"]
            # print(type(label))
            if type(label) == cst._nodes.expression.Name:
                # print(label.value)
                label = type_info["label"]
            elif type(label) == cst._nodes.expression.Attribute:
                # print(label)
                label = type_info["label"]
            # print(type(label))
            code_org = code
            # print(code_org)
            code_masked = mask_reveal(code_org, type_info)
            write_file("temp.py", code_masked)
            predict = pyright_infer("temp.py", type_info["dt"], type_info["name"])
            if predict is not None:
                predict["label"] = label
                t_list.append(predict)
                # print(predict)
            os.remove("temp.py")
    print(t_list)
    save_json("predictions1.json", t_list)
