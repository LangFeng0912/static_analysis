import libcst as cst
from cst_transformers import TypeAnnotationFinder, TypeAnnotationMasker
import json
from libsa4py.utils import write_file, read_file, list_files, save_json, find_repos_list, ParallelExecutor
from utils import pyright_infer
import os
from tqdm import tqdm
import time
from joblib import delayed
from datetime import timedelta


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


def process(project_path):
    project_author = project_path.split("/")[len(project_path.split("/")) - 2]
    project_name = project_path.split("/")[len(project_path.split("/")) - 1]
    id_tuple = (project_author, project_name)
    t_list = []
    files = list_files(project_path)
    for file in tqdm(files):
        # print(file)
        code = read_file(file)
        type_list = extract(code)
        # print(len(type_list))
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
            write_file(f"{project_author}{project_name}.py", code_masked)
            cur_time = time.time()
            predict = pyright_infer(f"{project_author}{project_name}.py", type_info["dt"], type_info["name"])
            if predict is not None:
                predict["label"] = label
                predict["time"] = str(timedelta(seconds=time.time() - cur_time))
                t_list.append(predict)
                # print(predict)
            os.remove(f"{project_author}{project_name}.py")
    print(len(t_list))
    json_path = f"{project_author}{project_name}_predict.json"
    save_json(os.path.join("/predict_dir", json_path), t_list)


def run(projects_path, repos_list, jobs=8, start=0):
    print(f"Number of projects to be processed: {len(repos_list)}")
    start_t = time.time()
    ParallelExecutor(n_jobs=jobs)(total=len(repos_list))(
        delayed(process)(os.path.join(projects_path, project["author"], project["repo"])) for i, project in
        enumerate(repos_list, start=start))
    print("Finished processing %d projects in %s " % (len(repos_list), str(timedelta(seconds=time.time() - start_t))))


def main():
    projects_path = "/data"
    repo_list = find_repos_list(projects_path)
    run(projects_path, repo_list)


if __name__ == '__main__':
    main()
