import re
from .post_order import PostOrderInterpreter


class ValidationInterpreter(PostOrderInterpreter):
    def __init__(self):
        super().__init__()
        self.precedences = {}

    def eval_Input(self, v):
        return v

    def eval_String(self, v):
        return v

    def eval_Number(self, v) -> float:
        return float(v)

    def eval_Value(self, v):
        return float(v)

    def eval_Char(self, v):
        return v

    def eval_conj(self, node, args) -> bool:
        '''Bool -> Bool, Bool;'''
        return args[0] and args[1]

    def eval_number(self, node, args) -> float:
        return float(args[0])

    def eval_len(self, node, args) -> int:
        return len(args[0])

    def eval_le(self, node, args) -> bool:
        return args[0] <= args[1]

    def eval_ge(self, node, args) -> bool:
        return args[0] >= args[1]

    def eval_Regex(self, v):
        return v

    def eval_Bool(self, v):
        return v

    def eval_re(self, node, args):
        self.precedences[node.production.id] = 4
        return fr'{args[0]}'

    def eval_unary_operator(self, arg, node, symbol):
        child_id = node.children[0].production.id
        child_prec = self.precedences[child_id]
        if child_prec >= self.precedences[node.production.id]:
            return f'{arg[0]}{symbol}'
        else:
            return f'({arg[0]}){symbol}'

    def eval_nary_operator(self, args, node, sep):
        children_str = []
        for child_idx in range(len(node.children)):
            child_id = node.children[child_idx].production.id
            child_prec = self.precedences[child_id]
            if child_prec >= self.precedences[node.production.id]:
                ch = f'{args[child_idx]}'
            else:
                ch = f'({args[child_idx]})'

            children_str.append(f'{ch}')
        children_str = sep.join(children_str)
        return children_str

    def eval_kleene(self, node, args):
        self.precedences[node.production.id] = 3
        return self.eval_unary_operator(args, node, '*')

    def eval_option(self, node, args):
        self.precedences[node.production.id] = 3
        return self.eval_unary_operator(args, node, '?')

    def eval_posit(self, node, args):
        self.precedences[node.production.id] = 3
        return self.eval_unary_operator(args, node, '+')

    def eval_copies(self, node, args):
        self.precedences[node.production.id] = 3
        child_id = node.children[0].production.id
        child_prec = self.precedences[child_id]
        if child_prec >= self.precedences[node.production.id]:
            return f'{args[0]}{{{args[1]}}}'
        else:
            return f'({args[0]}){{{args[1]}}}'

    def eval_concat(self, node, args):
        self.precedences[node.production.id] = 2
        return self.eval_nary_operator(args, node, '')

    def eval_union(self, node, args):
        self.precedences[node.production.id] = 1
        return self.eval_nary_operator(args, node, '|')

    def eval_match(self, node, args):
        match = re.fullmatch(args[0], args[1])
        return match is not None

    def eval_partial_match(self, node, args):
        match = re.match(args[0], args[1])
        return match is not None
