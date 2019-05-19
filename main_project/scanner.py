import sys
from error import *

"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        try:
            self.input_file = open(path, 'r')
        except (FileNotFoundError):
            print("Error: File doesn't exist in current directory")
            sys.exit()

        self.list_file = [line.rstrip('\n') for line in open(path, 'r')]

        """"Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.symbol_type_list = [self.HEADING, self.KEYWORD, self.NUMBER, 
                    self.NAME, self.COMMA, self.ARROW, self.NEW_LINE,
                    self.CURLY_OPEN, self.CURLY_CLOSE, self.DOT, self.EOF] = range(11)

        self.heading_list = ["devices", "init", "connections", "monitor"]
        [self.DEVICES_ID, self.INIT_ID, self.CONNECTION_ID, self.MONITOR_ID] = self.names.lookup(self.heading_list)

        self.keyword_list = ["are", "is", "have", "has", "to", "device"]
        [self.ARE, self.IS, self.HAVE, self.HAS,
        self.TO, self.DEVICE] = self.names.lookup(self.keyword_list)

        self.ignore = ["gate", "gates", "a", "an", "some", "initally"]

        self.current_character = ""
        self.current_line = 0
        self.character_number = 0
        self.word_number = 0

    def get_symbol(self, query=False):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces() # current character now not whitespace

        if self.current_character.isalpha(): # name
            name_list = self.get_name()
            self.name_string = name_list[0]

            if self.name_string in self.ignore:
                # ignore these words
                return None

            elif self.name_string.lower() in self.heading_list:
                symbol.type = self.HEADING
                symbol.id = self.names.query(self.name_string.lower())
            elif self.name_string in self.keyword_list:
                symbol.type = self.KEYWORD
                symbol.id = self.names.query(self.name_string)                
            else:
                symbol.type = self.NAME
                if query:
                    symbol.id = self.names.query(self.name_string)
                else:
                    [symbol.id] = self.names.lookup([self.name_string])
                
            print(self.name_string, end=' ')

        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER
            print(symbol.id[0],end=' ')

        elif self.current_character == "=" or self.current_character == '-': # punctuation
            if self.advance() == '>':
                symbol.type = self.ARROW
                self.advance()
            else:
                self.error(SyntaxError, "Unexpected symbol, expected '>")

        elif self.current_character == ",":
            symbol.type = self.COMMA
            self.advance()
        
        elif self.current_character == "\n":
            symbol.type = self.NEW_LINE
            self.advance()
            print("\n",end='')
 
        elif self.current_character == "{":
            symbol.type = self.CURLY_OPEN
            self.advance()
            print("{",end='')

        elif self.current_character == "}":
            symbol.type = self.CURLY_CLOSE
            self.advance()
            print("}")

        elif self.current_character == ":":
            self.advance()
            return None

        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == "": # end of file
            symbol.type = self.EOF

        else: # not a valid character
            self.error(SyntaxError, "Invalid character encountered")

        self.word_number += 1
        return symbol


    def get_name(self):
        """Seek the next name string in input_file.

        Return the name string (or None) and the next non-alphanumeric character.
        """
        name = self.current_character

        while True:
            self.current_character = self.advance()
            if self.current_character.isalnum():
                name = name + self.current_character
            else:
                return [name, self.current_character]


    def get_number(self):
        """Seek the next number in input_file.

        Return the number (or None) and the next non-numeric character.
        """
        num = self.current_character
        while True:
            self.current_character = self.advance()
            if self.current_character.isdigit():
                num = num+self.current_character
            else:
                return [num, self.current_character]

    
    def skip_spaces(self):
        """"advances until the character is no longer a space"""

        while self.current_character == ' ' or self.current_character == '\t':
            self.current_character = self.advance()


    def skip_newline(self):
        while self.advance() == '\n':
            pass

    def advance(self):
        """reads one further character into the document"""

        self.current_character = self.input_file.read(1)
        self.character_number += 1

        if self.current_character == '\n':
            self.current_line += 1
            self.character_number = self.word_number = 0
        
        return self.current_character

    def error(self, error_type, message=""):
        raise Error(message, error_type, self.list_file[self.current_line], 
                self.current_line, self.character_number)