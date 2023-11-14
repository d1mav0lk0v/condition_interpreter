"""Condition Interpreter.

TERM:
    IF
    TRUE
    FALSE
    THEN
    ELSE
    STRING
NOTE:
    STRING begins with a quote and ends with the first quote.
    Quote is a symbol `"`.

CONDITION:
    IF [TRUE | FALSE] THEN
        [STRING | CONDITION]
    ELSE
        [STRING | CONDITION]
NOTE:
    It is required to register a pair of IF and ELSE.
    Terms in the terms must be separated by at least one space.
    Spaces are ` `, \\t, \\v, \\n, \\r, \\f.

EBNF:
    <condition> =   "IF" <space> <boolean> <space> 
                    "THEN" <space>
                        ( <string> | <condition> ) <space>
                    "ELSE"
                        ( <string> | <condition> ) <space> ;
    <bolean>    =   "TRUE" | "FALSE" ;
    <space>     =   " " | "\\t" | "\\n" | "\\v" | "\\f" | "\\r" ;
    <string>    =   "\\"" { <char> } "\\"" ;
    <char>      =   <utf-8> - "\\""
"""


class TermBuilderError(SyntaxError):
    def __init__(self, msg: str, code_pos: int, code_len: int) -> None:
        self.msg = msg
        self.code_pos = code_pos
        self.code_len = code_len


    def __str__(self) -> str:
        return f"syntax error: {self.msg} in pos {self.code_pos}/{self.code_len}\n"


class ConditionInterpreter:
    def __init__(self, code: str) -> None:
        self.code = code
        self.__limit_level_condition = 10


    def run(self) -> str:
        self.__result = ""
        self.__mutable_result = True

        self.__code_pos = 0
        self.__code_len = len(self.code)

        self.__level_condition = 0

        # start with IF
        ok = self.__is_preffix("IF")
        self.__assert_syntax_error(ok, "expected IF")
        self.__code_pos = 0

        self.__condition()
        self.__endcode()

        return self.__result


    def __assert_syntax_error(self, ok: bool, msg: str) -> None:
        if ok:
            return None

        raise TermBuilderError(msg, self.__code_pos, self.__code_len)


    def __skip_space(self) -> None:
        p = self.__code_pos

        while p < self.__code_len and self.code[p].isspace():
            p += 1

        self.__code_pos = p


    def __is_preffix(self, preffix: str) -> bool:
        self.__skip_space()

        ok = self.code.startswith(preffix, self.__code_pos)
        p = self.__code_pos + len(preffix)

        if ok and (p == self.__code_len or self.code[p].isspace()):
            self.__code_pos = p
            return True

        return False


    def __is_preffix_string(self) -> bool:
        self.__skip_space()

        p = self.__code_pos

        if p == self.__code_len or self.code[p] != '"':
            return False

        i = 1
        while p + i < self.__code_len and self.code[p + i] != '"':
            i += 1
        i += 1

        if self.code[p + i - 1] == '"' \
                and (p + i == self.__code_len or self.code[p + i].isspace()):
            if self.__mutable_result:# and not self.__result:
                print(self.code[p:p+i])
                self.__result = self.code[p:p+i]
            self.__code_pos = p + i
            return True

        return False


    def __condition(self) -> bool:
        self.__level_condition += 1
        mutable_result = self.__mutable_result

        ok = (self.__level_condition <= self.__limit_level_condition)
        self.__assert_syntax_error(ok, "too many nested condition")

        ok = self.__is_preffix("IF")
        self.__assert_syntax_error(ok, "expected IF or STRING")

        ok_t = self.__is_preffix("TRUE")
        ok_f = self.__is_preffix("FALSE")
        ok = ok_t or ok_f
        self.__assert_syntax_error(ok, "expected TRUE or FALSE")

        ok = self.__is_preffix("THEN")
        self.__assert_syntax_error(ok, "expected THEN")

        self.__mutable_result = mutable_result and ok_t
        ok = self.__is_preffix_string() or self.__condition()

        ok = self.__is_preffix("ELSE")
        self.__assert_syntax_error(ok, "expected ELSE")

        self.__mutable_result = mutable_result and ok_f
        ok = self.__is_preffix_string() or self.__condition()

        self.__level_condition -= 1
        self.__mutable_result = mutable_result

        return ok


    def __endcode(self) -> bool:
        self.__skip_space()

        ok = (self.__code_pos == self.__code_len)
        self.__assert_syntax_error(ok, "expected ENDCODE")

        return ok
