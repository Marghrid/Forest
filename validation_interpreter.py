import sys

from tyrell.interpreter import PostOrderInterpreter


class ValidationInterpreter(PostOrderInterpreter):
    def check_integer(self, arg):
        if isinstance(arg, int):
            return True
        try:
            int(arg)
            return True
        except (TypeError, ValueError):
            return False

    def check_real(self, arg):
        if self.check_integer(arg): return False
        if isinstance(arg, float):
            return True
        try:
            float(arg)
            return True
        except (TypeError, ValueError):
            return False

    def eval_Regex(self, v):
        return v

    def eval_Input(self, v):
        return v

    def eval_String(self, v):
        return v

    def eval_Number(self, v) -> float:
        return float(v)

    def eval_Bool(self, v):
        return v

    def eval_MyNum(self, v):
        return int(v)

    def eval_conj(self, node, args) -> bool:
        '''Bool -> Bool, Bool;'''
        return args[0] and args[1]

    def eval_number(self, node, args) -> float:
        '''Number -> Input;'''
        return float(args[0])

    def eval_is_int(self, node, args) -> bool:
        '''Bool -> Input;'''
        return self.check_integer(args[0])

    def eval_is_real(self, node, args) -> bool:
        '''Bool -> Input;'''
        return self.check_real(args[0])

    def eval_is_string(self, node, args) -> bool:
        '''Bool -> Input;'''
        return isinstance(args[0], str) and self.check_integer(args[0]) and not self.check_real(args[0])

    def eval_string(self, node, args) -> str:
        '''String -> Input;'''
        return args[0]

    def eval_len(self, node, args) -> int:
        '''Number -> String;'''
        return len(args[0])

    def eval_le(self, node, args) -> bool:
        ''''Bool -> Number, Number;'''
        #print("le", args[0], args[1], args[0] <= args[1], file=sys.stderr)
        return args[0] <= args[1]

    def eval_ge(self, node, args) -> bool:
        '''Bool -> Number, Number;'''
        #print("ge", args[0], args[1], args[0] >= args[1], file=sys.stderr)
        return args[0] >= args[1]

    def apply_is_number(self, val) -> bool:
        return self.check_integer(val) or self.check_real(val)
