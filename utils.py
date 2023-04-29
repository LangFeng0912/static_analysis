import subprocess
import json
import re

var_pattern = r'Type of "(\w+)" is "(\w+)"'
func_pattern = r'Type of "(.+)" is "(.+)"'
param_pattern = r"(\w+): (\w+(?:\[.*?\])?)"


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
            if match and name == match.group(1):
                sig = match.group(2)
                # print(sig)
                predict_ret = sig.split(" -> ")[1]
                return dict(name=match.group(1), type=predict_ret, task="return")
            else:
                return None
        elif dt == "param":
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


def pyright_infer(file_path, dt: str, name: str):
    stdout, stderr, r_code = run_command("pyright %s --outputjson" % file_path, 60)
    output = json.loads(stdout)
    for dict in output["generalDiagnostics"]:
        if dict["severity"] == "information":
            t_dict = parse_pyright(dict, dt, name)
            if t_dict is not None:
                return t_dict