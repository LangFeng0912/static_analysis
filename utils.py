import subprocess
import json
import re
import os
from os.path import join, exists, isdir

var_pattern = r'Type of "(\w+)" is "(\w+)"'
func_pattern = r'Type of "(.+)" is "(.+)"'
param_pattern = r"(\w+): (\w+(?:\[.*?\])?)"
desp_pattern = r'^Revealed type \[-1\]: Revealed type for `([\w\.]+)` is `(.+?)`(?: \(inferred: `(.+?)`\))?\.$'

def run_command(cmd_args, timeout):
    process = subprocess.run(cmd_args, shell=True, capture_output=True, timeout=timeout)
    return process.stdout.decode(), process.stderr.decode(), process.returncode


def parse_pyright(p_dict, dt, name):
    type_str = p_dict["message"]
    if dt == "var":
        match = re.match(var_pattern, type_str)
        if match and name == match.group(1):
            return dict(name=match.group(1), type=match.group(2), task="var")
        else:
            return None

    else:
        if dt == "ret":
            # print(type_str)
            match = re.match(func_pattern, type_str)
            # print(name)
            # print(match.group(1))
            if match:
                sig = match.group(2)
                if "->" in sig:
                    predict_ret = sig.split(" -> ")[1]
                else:
                    predict_ret = sig
                return dict(name=match.group(1), type=predict_ret, task="return")
            else:
                return None
        elif dt == "param":
            # print(type_str)
            match = re.match(func_pattern, type_str)
            if match:
                param_sig = match.group(2).split(" -> ")[0]
                if len(param_sig) != 2:
                    un_quote = param_sig[1:-1]
                    matches = re.findall(param_pattern, un_quote)
                    for match_p in matches:
                        if name == match_p[0]:
                            return dict(name=match_p[0], type=match_p[1], task="parameter")

            else:
                return None
        else:
            return None

def parse_pyre(p_dict, dt, name):
    description = p_dict["description"]
    # print(description)
    match = re.match(desp_pattern, description)
    if match:
        print(match.group(1))
        print(match.group(2))
    else:
        print(description)


def start_pyre(project_path):
    if exists(join(project_path, '.watchmanconfig')):
        os.remove(join(project_path, '.watchmanconfig'))
    if exists(join(project_path, '.pyre_configuration')):
        os.remove(join(project_path, '.pyre_configuration'))
    pyre_dict = {
        "site_package_search_strategy": "pep561",
        "source_directories": [
            "."
        ],
        "workers": 127,
        "typeshed": "/pyre-check/stubs/typeshed/typeshed"
    }
    watchman_dict = {"root": "."}
    with open(join(project_path, '.watchmanconfig'), "w") as f:
        json.dump(watchman_dict, f)
    with open(join(project_path, '.pyre_configuration'), "w") as f_pyre:
        json.dump(pyre_dict, f_pyre)

    stdout, stderr, r_code = run_command("cd %s; watchman watch-project ." % project_path, 60)
    stdout_1, stderr_1, r_code_1 = run_command("cd %s; pyre start" % project_path, 60)
    if r_code == 0 and r_code_1 == 0:
        return True
    else:
        return False

def pyre_infer(project_path, file_path, dt, name):
    stdout, stderr, r_code = run_command("cd %s; pyre --output json" % project_path, 60)
    output = json.loads(stdout)
    for dict in output:
        if dict["name"]=="Revealed type":
            parse_pyre(dict, dt, name)



def pyright_infer(file_path, dt: str, name: str):
    stdout, stderr, r_code = run_command("pyright %s --outputjson" % file_path, 60)
    output = json.loads(stdout)
    for dict in output["generalDiagnostics"]:
        if dict["severity"] == "information":
            t_dict = parse_pyright(dict, dt, name)
            if t_dict is not None:
                return t_dict