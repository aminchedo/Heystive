import ast, operator as op
from .base import Skill
ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Mod: op.mod, ast.Pow: op.pow, ast.FloorDiv: op.floordiv, ast.USub: op.neg, ast.UAdd: op.pos}
def eval_expr(expr: str):
    def _e(n):
        if isinstance(n, ast.Expression): return _e(n.body)
        if isinstance(n, ast.Num): return n.n
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops: return ops[type(n.op)](_e(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in ops: return ops[type(n.op)](_e(n.left), _e(n.right))
        raise ValueError("invalid")
    tree = ast.parse(expr, mode="eval")
    return _e(tree)
class CalcSkill(Skill):
    name = "calc"
    def can_handle(self, text: str) -> bool:
        t = text.replace(" ", "")
        if not t: return False
        allowed = set("0123456789+-*/().%^")
        return all(c in allowed for c in t) and any(c in t for c in "+-*/")
    def handle(self, text: str, context: dict) -> dict:
        val = eval_expr(text)
        return {"expression": text, "result": val}