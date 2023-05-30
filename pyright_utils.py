"""
This script is use to make type from different models consistent
"""
import regex
import re
import subprocess
import json

var_pattern = r'Type of "(\w+)" is "(\w+)"'
func_pattern = r'Type of "(.+)" is "(.+)"'
param_pattern = r"(\w+): (\w+(?:\[.*?\])?)"

def make_types_consistent(t: str):
    """
    Removes typing module from type annotations
    """
    sub_regex = r'typing\.|typing_extensions\.|t\.|builtins\.|collections\.'

    def remove_quote_types(t: str):
        s = regex.search(r'^\'(.+)\'$', t)
        if bool(s):
            return s.group(1)
        else:
            # print(t)
            return t

    t = regex.sub(sub_regex, "", str(t))
    t = remove_quote_types(t)
    return t


def resolve_type_aliasing(t: str):
    """
    Resolves type aliasing and mappings. e.g. `[]` -> `list`
    """
    type_aliases = {'(?<=.*)any(?<=.*)|(?<=.*)unknown(?<=.*)': 'Any',
                    '^{}$|^Dict$|^Dict\[\]$|(?<=.*)Dict\[Any, *?Any\](?=.*)|^Dict\[unknown, *Any\]$': 'dict',
                    '^Set$|(?<=.*)Set\[\](?<=.*)|^Set\[Any\]$': 'set',
                    '^Tuple$|(?<=.*)Tuple\[\](?<=.*)|^Tuple\[Any\]$|(?<=.*)Tuple\[Any, *?\.\.\.\](?=.*)|^Tuple\[unknown, *?unknown\]$|^Tuple\[unknown, *?Any\]$|(?<=.*)tuple\[\](?<=.*)': 'tuple',
                    '^Tuple\[(.+), *?\.\.\.\]$': r'Tuple[\1]',
                    '\\bText\\b': 'str',
                    '^\[\]$|(?<=.*)List\[\](?<=.*)|^List\[Any\]$|^List$': 'list',
                    '^\[{}\]$': 'List[dict]',
                    '(?<=.*)Literal\[\'.*?\'\](?=.*)': 'Literal',
                    '(?<=.*)Literal\[\d+\](?=.*)': 'Literal',  # Maybe int?!
                    '^Callable\[\.\.\., *?Any\]$|^Callable\[\[Any\], *?Any\]$|^Callable[[Named(x, Any)], Any]$': 'Callable',
                    '^Iterator[Any]$': 'Iterator',
                    '^OrderedDict[Any, *?Any]$': 'OrderedDict',
                    '^Counter[Any]$': 'Counter',
                    '(?<=.*)Match[Any](?<=.*)': 'Match'}

    def resolve_type_alias(t: str):
        for t_alias in type_aliases:
            if regex.search(regex.compile(t_alias), t):
                t = regex.sub(regex.compile(t_alias), type_aliases[t_alias], t)
        return t

    return resolve_type_alias(t)


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


def run_command(cmd_args, timeout):
    process = subprocess.run(cmd_args, shell=True, capture_output=True, timeout=timeout)
    return process.stdout.decode(), process.stderr.decode(), process.returncode

def pyright_infer(file_path, dt: str, name: str):
    try:
        stdout, stderr, r_code = run_command("pyright %s --outputjson" % file_path, 60)
        output = json.loads(stdout)
        for dict in output["generalDiagnostics"]:
            if dict["severity"] == "information":
                t_dict = parse_pyright(dict, dt, name)
                if t_dict is not None:
                    return t_dict
    except Exception as e:
        print(str(e))
        pass

