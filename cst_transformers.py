import libcst as cst
from libcst.metadata import PositionProvider, CodeRange


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
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self):
        super().__init__()
        self.annotated_types = []
        self.var_list = set()

    def __get_line_column_no(self, node):
        lc = self.get_metadata(cst.metadata.PositionProvider, node)
        return (lc.start.line, lc.start.column), (lc.end.line, lc.end.column)

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
        for statement in original_node.body.body:
            if type(statement.body[0]) == cst.AnnAssign:
                # print(statement.body[0])
                # print(ranges[statement.body[0]].start)
                type_dict = dict(dt="var", func_name=original_node.name.value, name=statement.body[0].target.value,
                                 label=statement.body[0].annotation.annotation.value)
                self.annotated_types.append(type_dict)
                self.var_list.add(self.__get_line_column_no(statement.body[0]))

    def visit_AnnAssign(self, node: cst.AnnAssign) -> None:
        pos = self.__get_line_column_no(node)
        if pos not in self.var_list:
            type_dict = dict(dt="var", func_name="__global", name=node.target.value,
                                 label=node.annotation.annotation.value)
            self.annotated_types.append(type_dict)

    # def visit_Param(self, original_node: cst.Param):
    #     if original_node.annotation is not None:
    #         print(f"{original_node.name.value}: {original_node.annotation.annotation.value}")
    #         # self.annotated_params.append(original_node)
    # def visit_AnnAssign(self, original_node: cst.AnnAssign):
    #     if original_node.annotation is not None:
    #         print(f"{original_node.target.value}: {original_node.annotation.annotation.value}")

