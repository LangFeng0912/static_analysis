from libsa4py.utils import load_json, save_json
from utils.pyright import merge_vars, merge_params, merge_returns

pyright_res = load_json("/home/lang/hybrid_infer/0x0FB0pulsar_predict.json")
ml_res = load_json("/home/lang/hybrid_infer/0x0FB0pulsar_mlInfer.json")

project_id = "0x0FB0/pulsar"


def merge_file(sa_file, ml_file):
    filtered_list = [d for d in sa_file if d.get('type') != 'Unknown']
    var_preds = [d for d in filtered_list if d.get("task") == 'var']
    param_preds = [d for d in filtered_list if d.get("task") == "parameter"]
    ret_preds = [d for d in filtered_list if d.get("task") == "return"]

    merged_file = merge_vars(var_preds, ml_file, "model")

    if "funcs" in ml_file.keys():
        func_list = merged_file['funcs']
        func_list_1 = merged_file['funcs']
        for i in range(len(func_list)):
            merged_func = merge_vars(var_preds, func_list[i], "func")
            func_list_1[i] = merged_func
            merged_func = merge_params(param_preds, func_list[i])
            func_list_1[i] = merged_func
            merged_func = merge_returns(ret_preds, func_list[i])
            func_list_1[i] = merged_func

        merged_file['funcs'] = func_list_1

    if "classes" in ml_file.keys():
        class_list = merged_file['classes']
        class_list_1 = merged_file['classes']
        for i in range(len(class_list)):
            class_list_1[i] = merge_vars(var_preds, class_list[i], "class")
            if "funcs" in class_list_1[i].keys():
                func_list = class_list[i]['funcs']
                func_list_1 = class_list_1[i]['funcs']
                for j in range(len(func_list)):
                    merged_func = merge_vars(var_preds, func_list[j], "func")
                    func_list_1[j] = merged_func
                    merged_func = merge_params(param_preds, func_list[j])
                    func_list_1[j] = merged_func
                    merged_func = merge_returns(ret_preds, func_list[j])
                    func_list_1[j] = merged_func

                class_list_1[i]['funcs'] = func_list_1
        merged_file['classes'] = class_list_1

    return merged_file


def merge_project(sa_dict, ml_dict):
    merged_dict = {}
    for key in ml_dict:
        if key in sa_dict.keys():
            m_file = merge_file(sa_dict[key], ml_dict[key])
            merged_dict[key] = m_file
        else:
            merged_dict[key] = ml_dict[key]
    return merged_dict


def update_key(file_name, project_id):
    author = project_id.split("/")[0]
    repo = project_id.split("/")[1]
    list = file_name.split("/")
    start_index = 0
    for i in range(len(list) - 1):
        if list[i] == author and list[i + 1] == repo:
            start_index = i
            break
    new_list = []
    new_list.append("data")
    while start_index < len(list):
        new_list.append(list[start_index])
        start_index = start_index + 1
    return "/".join(new_list)


def merge(ml_dict, static_dict, project_id):
    src_dict = {}
    src_dict_ml = {}
    for p_dict in static_dict:
        key = list(p_dict.keys())[0]
        key_new = update_key(key, project_id)
        src_dict[key_new] = p_dict[key]
    for key in ml_dict[project_id]['src_files'].keys():
        key_new = update_key(key, project_id)
        src_dict_ml[key_new] = ml_dict[project_id]['src_files'][key]

    merged_project: dict = {project_id: {"src_files": {}}}
    print(len(src_dict))
    print(len(src_dict_ml))
    merged_src_dict = merge_project(src_dict, src_dict_ml)
    merged_project[project_id]["src_files"] = merged_src_dict
    return merged_project


if __name__ == '__main__':
    merged_src = merge(ml_res, pyright_res, project_id)
    save_json("/home/lang/hybrid_infer/0x0FB0pulsar_pyrighth.json", merged_src)