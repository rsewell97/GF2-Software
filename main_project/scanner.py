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

    def __init__(self, path, names, string=False):
        """Open specified file and initialise reserved words and IDs."""
        self.total_errors = 0

        if string:
            self.read_as_string = True
            self.total_error_string = ""
            self.input_file = path
            self.list_file = [line.rstrip('\n') for line in self.input_file.split('\n')]
            self.character_count = 0
        else:
            self.read_as_string = False
            try:
                self.input_file = open(path, 'r')
            except FileNotFoundError:
                raise FileNotFoundError ("Error: File doesn't exist in current directory")
                sys.exit()
            self.list_file = [line.rstrip('\n') for line in open(path, 'r')]

        """"Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.symbol_type_list = [self.HEADING, self.KEYWORD, self.NUMBER, 
                    self.NAME, self.COMMA, self.ARROW, self.CURLY_OPEN, 
                    self.CURLY_CLOSE, self.SEMICOLON, self.DOT, self.MINUS, 
                    self.SLASH, self.HASHTAG, self.EOF] = range(14)

        self.heading_list = ["devices", "connections", "monitor"]
        [self.DEVICES_ID, self.CONNECTION_ID, self.MONITOR_ID] = self.names.lookup(self.heading_list)

        self.keyword_list = ["are", "is", "have", "has", "set", "to", "cycle", "trace"]
        [self.ARE, self.IS, self.HAVE, self.HAS, self.SET,
        self.TO, self.CYCLE, self.TRACE] = self.names.lookup(self.keyword_list)

        [self.DEVICE] = self.names.lookup(["device"])

        self.ignore = ["gate", "gates", "a", "an", "some", "initially", "inputs", "connected"]
        self.stopping_symbols = [self.SEMICOLON, self.CURLY_CLOSE, self.EOF]

        self.current_character = " "
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
                return None
            elif self.name_string.lower() in self.heading_list:
                symbol.type = self.HEADING
                symbol.id = self.names.query(self.name_string.lower())
            elif self.name_string in self.keyword_list:
                symbol.type = self.KEYWORD
                symbol.id = self.names.query(self.name_string)
            elif self.name_string.lower() == self.names.get_name_string(self.DEVICE):
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

        elif self.current_character == "=": # punctuation
            if self.advance() == '>':
                symbol.type = self.ARROW
                self.advance()
            else:
                self.error(SyntaxError, "Unexpected symbol, expected '>")

        elif self.current_character == ",":
            symbol.type = self.COMMA
            self.advance()
 
        elif self.current_character == "{":
            symbol.type = self.CURLY_OPEN
            self.advance()
            print("{",end='')

        elif self.current_character == "}":
            symbol.type = self.CURLY_CLOSE
            self.advance()
            print("}")

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()
            print(";")

        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()
        
        elif self.current_character == "-": 
            symbol.type = self.MINUS
            self.advance()
            
        elif self.current_character == "": # end of file
            symbol.type = self.EOF
            
        
        
        elif self.current_character == "#": # single line comment
            x = 0
            symbol.type = self.HASHTAG
            while x < 1:
                self.advance()
                while self.current_character != "\n": # ignore until end of line
                    self.advance()
                x += 1
        
        elif self.current_character == "/": #bulk comment, expect another
            symbol.type = self.SLASH
            self.advance()
            if self.current_character == "/": # start bulk comment, start ignoring
                no_consec_slashes = 0
                while no_consec_slashes < 2: # ignore until two consecutive slashes
                    self.advance()
                    if self.current_character == "/":
                        no_consec_slashes += 1
                    elif self.current_character == "":
                        self.error(SyntaxError, "Reached end of file while still in a bulk comment")
                        break
                    else:
                        no_consec_slashes = 0
            """else:
                self.error(SyntaxError, "Unexpected symbol, expected '//' at beginning of bulk comment")"""
        
        elif self.current_character == "-": #minus sign
            self.error(SyntaxError, "Unexpected symbol, negative numbers not allowed")
        
        else: # not a valid character
            self.error(SyntaxError, "Invalid character encountered")

        self.word_number += 1
        return symbol

    def ignore(until): #will ignore all characters until character until is found
        until = str(until)
        while self.current_character != until:
            self.advance()
        return

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

        while self.current_character.isspace():
            self.current_character = self.advance()


    def advance(self):
        """reads one further character into the document"""
        if self.read_as_string:
            try:
                self.current_character = self.input_file[self.character_count]
            except IndexError:
                self.current_character = ""
                return self.current_character
            self.character_count += 1
        else:
            self.current_character = self.input_file.read(1)

        self.character_number += 1

        if self.current_character == '\n':
            self.current_line += 1
            self.character_number = self.word_number = 0
        
        return self.current_character

    def error(self, error_type, message=""):
       # print(__name__)
        self.total_errors += 1

        if self.read_as_string:
            self.total_error_string += Error(message, error_type, self.list_file[self.current_line], 
                    self.current_line, self.character_number).error_string
        else:
            try:
                Error(message, error_type, self.list_file[self.current_line], 
                        self.current_line, self.character_number)
            except IndexError:
                Error(message, error_type, self.list_file[-1], 
                        self.current_line, self.character_number)
        
        while True:
            self.symbol = self.get_symbol()
            if self.symbol is None:
                continue
            if self.symbol.type in self.stopping_symbols:
                break
            elif self.read_as_string:
                try:
                    Error(message, error_type, self.list_file[self.current_line], 
                        self.current_line, self.character_number)
                except IndexError:
                    break
        
				
        return error_type
    
