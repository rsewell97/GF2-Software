import sys
sys.tracebacklimit=0

class SemanticError(Exception):
    pass
        
        
class Error(Exception):
    def __init__(self, message, error, line, line_num, char):

        # Call the base class constructor with the parameters it needs
        super().__init__(message+'\n')
        
        if error == SemanticError:
            print("\n\nSemanticError ", end='')
        elif error == SyntaxError:
            print("\n\nSyntaxError ", end='')
                
        print("""on line {}:
        {}
        """.format(line_num+1, line),end='')
        print(char*' '+'^')
