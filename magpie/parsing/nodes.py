import abc


class Expr(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def evaluate(self, context):
        pass

    def visit(self, visitor):
        visitor(self)

    def rewrite(self, visitor):
        return visitor(self)

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def evaluate(self, context):
        return self.value

class ListLiteral(Expr):
    def __init__(self, values):
        self.values = values

    def __str__(self):
        tmp = ', '.join(str(v) for v in self.values)
        return f'[{tmp}]'

    def evaluate(self, context):
        return [value.evaluate(context) for value in self.values]

    def visit(self, visitor):
        visitor(self)
        for value in self.values:
            value.visit(visitor)

class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def evaluate(self, context):
        return context[self.name]

class UnaryOp(Expr):
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def __str__(self):
        glue, end = '', ''
        if self.op == 'not':
            glue += ' '
        if isinstance(self.right, BinaryOp):
            glue += '('
            end = ')'
        return f'{self.op}{glue}{self.right}{end}'

    def evaluate(self, context):
        val = self.right.evaluate(context)
        match self.op:
            case '-':
                return -val
            case 'not':
                return not val
        msg = f'Unknown unary operator: {self.op}'
        raise ValueError(msg)

    def visit(self, visitor):
        self.right.visit(visitor)
        visitor(self)

    def rewrite(self, visitor):
        right = self.right.rewrite(visitor)
        return visitor(self.__class__(self.op, right))

class BinaryOp(Expr):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        if self.op == '/' and isinstance(self.right, Literal) and self.right.value == 0:
            raise ZeroDivisionError

    def __str__(self):
        op, lglue, rglue, end = '', '', '', ''
        letterop = self.op in {'and', 'or', 'xor', 'if', 'iif'}
        compop = self.op in {'>', '<', '>=', '<=', '==', '!='}
        lowmathop = self.op in {'=', '+', '-'}
        if lowmathop or letterop or compop:
            lglue, rglue = ' ', ' '
        if isinstance(self.left, BinaryOp) and (letterop or (self.op == '/') or (self.op == '*' and self.left.op in {'+', '-'})):
            op = f'{op}('
            lglue = f'){lglue}'
        if isinstance(self.left, UnaryOp) and letterop:
            op = f'{op}('
            lglue = f'){lglue}'
        if isinstance(self.right, BinaryOp) and (letterop or (self.op == '/') or (self.op == '*' and self.right.op in {'+', '-'})):
            rglue = f'{rglue}('
            end = ')'
        if isinstance(self.right, UnaryOp) and letterop:
            rglue = f'{rglue}('
            end = ')'
        if self.op == '*' and isinstance(self.left, Literal):
            if self.left.value == -1:
                return f'{op}-{lglue}{rglue}{self.right}{end}'
            if self.left.value == 1:
                return f'{op}{lglue}{rglue}{self.right}{end}'
        return f'{op}{self.left}{lglue}{self.op}{rglue}{self.right}{end}'

    def evaluate(self, context):
        lval = self.left.evaluate(context)
        rval = self.right.evaluate(context)
        match self.op:
            case '+':
                return lval + rval
            case '-':
                return lval - rval
            case '*':
                return lval * rval
            case '**':
                return lval ** rval
            case '<':
                return lval < rval
            case '>':
                return lval > rval
            case '/':
                return lval / rval
            case '==':
                return lval == rval
            case '!=':
                return lval != rval
            case '<=':
                return lval <= rval
            case '>=':
                return lval >= rval
            case 'and':
                return lval and rval
            case 'or':
                return lval or rval
            case 'xor':
                return lval != rval
            case 'if':
                return lval or (not rval)
            case 'iif':
                return lval == rval
            case 'in':
                return lval in rval
            case 'not in':
                return lval not in rval
        msg = f'Unknown binary operator: {self.op}'
        raise ValueError(msg)

    def visit(self, visitor):
        self.left.visit(visitor)
        self.right.visit(visitor)
        visitor(self)

    def rewrite(self, visitor):
        left = self.left.rewrite(visitor)
        right = self.right.rewrite(visitor)
        return visitor(self.__class__(self.op, left, right))
