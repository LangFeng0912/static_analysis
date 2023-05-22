import regex


def type_consist(t: str):
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


def check(t: str):
    types = ["", "Any", "any", "None", "Object", "object", "type", "Type[Any]",
             'Type[cls]', 'Type[type]', 'Type', 'TypeVar', 'Optional[Any]']
    if t in types:
        return False
    else:
        return True


def merge_vars(var_dict_sa, ml_dict, range):
    # add = 0
    # var_dict_sa = sa_dict["variables"]
    if "variables_p" in ml_dict.keys():
        var_dict_1 = ml_dict["variables_p"]
    else:
        var_dict_1 = {}
    for var_slot in var_dict_sa:
        var_name = var_slot["name"]
        var_pred = type_consist(var_slot["type"])
        var_pred = resolve_type_aliasing(var_pred)
        # var_dict_sa[var_key] = type_consist(var_dict_sa[var_key])
        if check(var_pred):
            if range == "model":
                if var_name in var_dict_1.keys() and var_slot["loc"] == ml_dict["mod_var_ln"][var_name]:
                    if len(var_dict_1[var_name]) != 0 and var_dict_1[var_name][0][0] != var_pred:
                        print(var_slot)
                        sa_type = [var_pred, 1.2]
                        var_dict_1[var_name].insert(0, sa_type)
            if range == "func":
                if var_name in var_dict_1.keys() and var_slot["loc"] == ml_dict["fn_var_ln"][var_name]:
                    if len(var_dict_1[var_name]) != 0 and var_dict_1[var_name][0][0] != var_pred:
                        print(var_slot)
                        sa_type = [var_pred, 1.2]
                        var_dict_1[var_name].insert(0, sa_type)
            if range == "class":
                if var_name in var_dict_1.keys() and var_slot["loc"] == ml_dict["cls_var_ln"][var_name]:
                    if len(var_dict_1[var_name]) != 0 and var_dict_1[var_name][0][0] != var_pred:
                        print(var_slot)
                        sa_type = [var_pred, 1.2]
                        var_dict_1[var_name].insert(0, sa_type)
    ml_dict["variables_p"] = var_dict_1
    return ml_dict


def merge_params(param_dict_sa, ml_dict):
    if "params_p" in ml_dict.keys():
        param_dict_1 = ml_dict["params_p"]
    else:
        param_dict_1 = {}

    for param_slot in param_dict_sa:
        param_name = param_slot["name"]
        if param_slot["loc"] == ml_dict["fn_lc"] and param_name in param_dict_1.keys():
            type_pred = type_consist(param_slot["type"])
            type_pred = resolve_type_aliasing(type_pred)
            if len(param_dict_1[param_name]) != 0 and param_dict_1[param_name][0][0] != type_pred:
                print(param_slot)
                sa_type = [type_pred, 1.2]
                param_dict_1[param_name].insert(0, sa_type)
    ml_dict["params_p"] = param_dict_1
    return ml_dict


def merge_returns(ret_dict_sa, ml_dict):
    if "ret_type_p" in ml_dict.keys():
        ret_type_1 = ml_dict["ret_type_p"]
    else:
        ret_type_1 = []
    for ret_slot in ret_dict_sa:
        ret_name = ret_slot["name"]
        if ret_slot["loc"] == ml_dict["fn_lc"]:
            type_pred = type_consist(ret_slot["type"])
            type_pred = resolve_type_aliasing(type_pred)
            if len(ret_type_1) != 0 and ret_type_1[0][0] != type_pred:
                print(ret_slot)
                sa_type = [type_pred, 1.2]
                ret_type_1.insert(0, sa_type)
    ml_dict["ret_type_p"] = ret_type_1
    return ml_dict
