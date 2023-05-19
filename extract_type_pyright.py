from libsa4py.utils import write_file, read_file, list_files, save_json, find_repos_list, ParallelExecutor
import libcst as cst
from cst_transformers import TypeAnnotationFinder, TypeAnnotationMasker
from libsa4py.exceptions import ParseError
import os
from tqdm import tqdm
from pyright_utils import make_types_consistent, pyright_infer

filtered_types = ['Any', 'None', 'object', 'type', 'Type[Any]', 'Type[cls]', 'Type[type]', 'Type', 'TypeVar',
                  'Optional[Any]']


def extract(code):
    parsed_program = cst.parse_module(code)
    transformer = TypeAnnotationFinder()
    new_tree = cst.metadata.MetadataWrapper(parsed_program).visit(transformer)
    return transformer.annotated_types


def mask_reveal(code, type):
    parsed_program = cst.parse_module(code)
    transformer_mask = TypeAnnotationMasker(type)
    new_tree = cst.metadata.MetadataWrapper(parsed_program).visit(transformer_mask)
    return new_tree.code


def process(project_path):
    project_author = project_path.split("/")[len(project_path.split("/")) - 2]
    project_name = project_path.split("/")[len(project_path.split("/")) - 1]
    id_tuple = (project_author, project_name)
    t_list = []
    files = list_files(project_path)
    for file in tqdm(files):
        try:
            pre_list = []
            code = read_file(file)
            type_list = extract(code)
            for type_info in type_list:
                label = make_types_consistent(type_info["label"])
                if label in filtered_types:
                    continue
                code_org = code
                code_masked = mask_reveal(code_org, type_info)
                write_file(f"{project_author}{project_name}.py", code_masked)
                predict = None
                # for pyright
                predict = pyright_infer(f"{project_author}{project_name}.py", type_info["dt"], type_info["name"])
                if predict is not None:
                    predict["label"] = label
                    predict["loc"] = type_info["loc"]
                    pre_list.append(predict)
                os.remove(f"{project_author}{project_name}.py")
            if len(pre_list) != 0:
                t_list.append({file: pre_list})
        except ParseError as err:
            print(err)
        except UnicodeDecodeError:
            print(f"Could not read file {file}")

    # print(len(t_list))
    json_path = f"{project_author}{project_name}_predict.json"
    save_json(os.path.join("/predict_dir", json_path), t_list)


if __name__ == '__main__':
    path = "/dataset/0x0FB0/pulsar"
    process(path)