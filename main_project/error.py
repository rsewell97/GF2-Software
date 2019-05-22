import sys

class SemanticError(Exception):
    pass
        
        
class Error(Exception):
    def __init__(self, message, error, line, line_num, char):

        # Call the base class constructor with the parameters it needs
        super().__init__(message+'\n')
        
        if error == SemanticError:
            error_type = "SemanticError"
        elif error == SyntaxError:
            error_type = "SyntaxError"
        elif error == ValueError:
            error_type = "ValueError"
        else:
            error_type = "Error"
        
        self.error_string = """Error on line {line_num}:
    {line}
    {char}^
{error_type}: {msg}\n""".format(error_type=error_type,
                    line_num = line_num+1,
                    line=line,
                    char=char*' ',
                    msg= message)
        self.error_string += '-'*30+'\n'
        print(self.error_string)