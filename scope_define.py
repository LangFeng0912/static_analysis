import libcst as cst
from libcst.metadata import ScopeProvider, SymbolTable

class MyCSTVisitor(cst.CSTVisitor):
    def __init__(self, symbol_table):
        super().__init__()
        self.scope_provider = ScopeProvider(symbol_table)

    def visit_AnnAssign(self, node: cst.AnnAssign) -> None:
        is_local = self.scope_provider.is_local_definition(node.target)
        print(f"Visited AnnAssign with target: {node.target}, is_local={is_local}")

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.scope_provider = self.scope_provider.get_inner_scope_provider(node)

# Define a code snippet to traverse
code = """
x = 0
def my_function(y: int):
    z: str = "hello"
"""

# Parse the code snippet into a CST node
module = cst.parse_module(code)

# Analyze the module's symbol table to get scope information
symbol_table = SymbolTable.build_global_symbol_table(module)

# Traverse the CST node with MyCSTVisitor, passing the symbol table as an argument
visitor = MyCSTVisitor(symbol_table)
module.visit(visitor)
