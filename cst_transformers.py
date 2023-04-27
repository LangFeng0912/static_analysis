import libcst as cst


class TypeAnnotationFinder(cst.CSTTransformer):
    """
    It find all type annotations from a source code
    use a dict object for saving the type information:
    for example:
        {
            dt: "param",
            func_name: "my_foo",
            name: "foo",
            label: "Fool"
        }
    """

    def __init__(self):
        super().__init__()
        self.annotated_types = []

    def visit_FunctionDef(self, original_node: cst.FunctionDef):
        # print(original_node)
        if original_node.returns is not None:
            # print(f"{original_node.name.value}: {original_node.returns.annotation.value}")
            type_dict = dict(dt="ret", func_name=original_node.name.value, name="ret_type",
                             label=original_node.returns.annotation.value)
            self.annotated_types.append(type_dict)
            # annotated_functions.append(original_node)
        for param in original_node.params.params:
            # print(param)
            if param.annotation is not None:
                type_dict = dict(dt="param", func_name=original_node.name.value, name=param.name.value,
                                 label=param.annotation.annotation.value)
                self.annotated_types.append(type_dict)
        for statement in original_node.body:
            # print(statement.body)
            print(cst.ensure_type(statement.body, cst.AnnAssign).value)
            if isinstance(statement.body, cst.AnnAssign):
                type_dict = dict(dt="var", func_name=original_node.name.value, name=statement.body.target.value,
                                 label=statement.body.annotation.annotation.value)
                self.annotated_types.append(type_dict)

    def visit_AnnAssign(self, node: cst.AnnAssign) -> None:
        print(f"Visited AnnAssign with target: {node.target}")

    # def visit_Param(self, original_node: cst.Param):
    #     if original_node.annotation is not None:
    #         print(f"{original_node.name.value}: {original_node.annotation.annotation.value}")
    #         # self.annotated_params.append(original_node)
    # def visit_AnnAssign(self, original_node: cst.AnnAssign):
    #     if original_node.annotation is not None:
    #         print(f"{original_node.target.value}: {original_node.annotation.annotation.value}")

