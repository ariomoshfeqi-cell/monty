
import ast
import io
import operator
import random


MAX_STEPS = 10_000
MAX_OUTPUT = 20_000

SAFE_FUNCTIONS = {
    "number": int,
    "integer": int,
    "text": str,
    "mword": str,
    "decimal": float,
    "length": len,
    "spam": sum,
    "every": all,
    "end": max,
    "maximum": max,
    "minimum": min,
    "sort": sorted,
    "absolute": abs,
    "roundnum": round,
    "pows": pow,
}

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

COMPARISON_OPERATORS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class MontyError(Exception):
    pass


class MontyEngine:
    def __init__(self, inputs=None, max_output=None):
        self.variables = {
            "egg": True,
            "chicken": False,
            "monty": "python",
            "python": "monty",
        }

        self.max_output = max_output
        self.inputs = inputs or []
        self.input_index = 0
        self.output = io.StringIO()
        self.steps = 0

        self.functions = dict(SAFE_FUNCTIONS)
        self.functions.update({
            "pt": self.print_output,
            "show": self.print_output,
            "inp": self.get_input,
            "ask": self.get_input,
            "sequence": self.safe_range,
            "random_number": random.randint,
        })

    def print_output(self, *values):
        text = " ".join(str(value) for value in values) + "\n"

        if self.max_output is not None:
            if self.output.tell() + len(text) > self.max_output:
                raise MontyError("Output limit reached.")

        self.output.write(text)

    def get_input(self, prompt=""):
        if self.input_index >= len(self.inputs):
            raise MontyError("INPUT_NEEDED:" + str(prompt))

        answer = self.inputs[self.input_index]
        self.input_index += 1
        return answer

    def safe_range(self, *args):
        result = range(*args)

        if len(result) > 1000:
            raise MontyError("Range is too large.")

        return result

    def tick(self):
        self.steps += 1

        if self.steps > MAX_STEPS:
            raise MontyError("Monty step limit reached.")

    def evaluate(self, node):
        self.tick()

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, int, float, bool, type(None))):
                return node.value

            raise MontyError("Unsupported value.")

        if isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]

            raise MontyError(f"Unknown variable: {node.id}")

        if isinstance(node, ast.List):
            return [self.evaluate(item) for item in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self.evaluate(item) for item in node.elts)

        if isinstance(node, ast.Dict):
            return {
                self.evaluate(key): self.evaluate(value)
                for key, value in zip(node.keys, node.values)
            }

        if isinstance(node, ast.BinOp):
            operation = BINARY_OPERATORS.get(type(node.op))

            if operation is None:
                raise MontyError("Unsupported math operation.")

            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise MontyError("Exponent is too large.")

            result = operation(left, right)

            if isinstance(result, (str, list, tuple)) and len(result) > 20000:
                raise MontyError("Result is too large.")

            return result

        if isinstance(node, ast.UnaryOp):
            value = self.evaluate(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return +value

            if isinstance(node.op, ast.Not):
                return not value

            raise MontyError("Unsupported unary operation.")

        if isinstance(node, ast.Compare):
            left = self.evaluate(node.left)

            for operation_node, comparator in zip(
                node.ops, node.comparators
            ):
                operation = COMPARISON_OPERATORS.get(type(operation_node))

                if operation is None:
                    raise MontyError("Unsupported comparison.")

                right = self.evaluate(comparator)

                if not operation(left, right):
                    return False

                left = right

            return True

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self.evaluate(value) for value in node.values)

            if isinstance(node.op, ast.Or):
                return any(self.evaluate(value) for value in node.values)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise MontyError("Only approved function calls are allowed.")

            name = node.func.id

            if name == "vachange":
                if (
                    len(node.args) != 2
                    or not all(isinstance(arg, ast.Name) for arg in node.args)
                ):
                    raise MontyError(
                        "Use vachange(old_name, new_name)."
                    )

                old_name = node.args[0].id
                new_name = node.args[1].id

                if old_name not in self.variables:
                    raise MontyError(f"Unknown variable: {old_name}")

                if new_name in self.variables:
                    raise MontyError(f"Variable already exists: {new_name}")

                self.variables[new_name] = self.variables.pop(old_name)
                return None

            function = self.functions.get(name)

            if function is None:
                raise MontyError(f"Function not allowed: {name}")

            arguments = [self.evaluate(arg) for arg in node.args]

            if node.keywords:
                raise MontyError("Keyword arguments are not supported.")

            return function(*arguments)

        raise MontyError(
            f"Unsupported expression: {type(node).__name__}"
        )

    def execute_statement(self, node):
        self.tick()

        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(
                node.targets[0], ast.Name
            ):
                raise MontyError(
                    "Only simple variable assignments are allowed."
                )

            name = node.targets[0].id
            self.variables[name] = self.evaluate(node.value)
            return

        if isinstance(node, ast.Expr):
            self.evaluate(node.value)
            return

        if isinstance(node, ast.If):
            condition = self.evaluate(node.test)
            statements = node.body if condition else node.orelse

            for statement in statements:
                self.execute_statement(statement)

            return

        raise MontyError(
            f"Unsupported statement: {type(node).__name__}"
        )

    def run(self, code):
        try:
            tree = ast.parse(code)

            if len(tree.body) > 500:
                raise MontyError("Too many statements.")

            for statement in tree.body:
                self.execute_statement(statement)

            return {
                "output": self.output.getvalue(),
                "done": True,
                "website_html": None,
            }

        except MontyError as error:
            message = str(error)

            if message.startswith("INPUT_NEEDED:"):
                return {
                    "output": self.output.getvalue(),
                    "inputNeeded": message[len("INPUT_NEEDED:"):],
                }

            return {
                "output": self.output.getvalue()
                + "\nMontyError: " + message,
                "done": True,
                "website_html": None,
            }

        except Exception as error:
            return {
                "output": self.output.getvalue()
                + f"\n{type(error).__name__}: {error}",
                "done": True,
                "website_html": None,
            }


def run_monty(code, inputs=None, max_output=None):
    engine = MontyEngine(inputs, max_output)
    return engine.run(code)

