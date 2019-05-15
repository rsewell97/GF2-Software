import sys
sys.tracebacklimit=0

class SemanticError(Exception):
    def __init__(self):
        print("\n\nSemanticError ", end='')


class SyntaxError(Exception):
    def __init__(self):
        print("\n\nSyntaxError ", end='')


class Error(Exception):
    def __init__(self, message, errors, line, line_num, char):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        
        if errors == SemanticError:
            SemanticError()
        elif errors == SyntaxError:
            SyntaxError()
                
        print("""on line {}:
        {}
        """.format(line_num+1, line),end='')
        print(char*' '+'^')
