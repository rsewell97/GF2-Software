#!/usr/bin/env python3
import sys

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
        except (FileNotFoundError, IsADirectoryError):
            print("Error: File doesn't exist in current directory")
            sys.exit()

        self.list_file = [line.rstrip('\n') for line in open(path, 'r')]


        """"Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
        self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(7)
        self.keywords_list = ["DEVICES", "CONNECT", "MONITOR", "END"]

        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,self.END_ID] = self.names.lookup(self.keywords_list)

        self.current_character = ""



    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces() # current character now not whitespace

        if self.current_character.isalpha(): # name
            name_string = self.get_name()

            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
                [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == "=": # punctuation
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",":
        # etc for other punctuation
            pass
        elif self.current_character == "": # end of file
            symbol.type = self.EOF
        else: # not a valid character
            self.advance()
        return symbol


    def get_name(self):
        """Seek the next name string in input_file.

        Return the name string (or None) and the next non-alphanumeric character.
        """
        while True:
            char = self.input_file.read(1)
            if char.isalpha():
                name = char
                while True:
                    char = self.input_file.read(1)
                    if char.isalnum():
                        name = name+char
                    else:
                        return [name, char]

            elif char == '':
                return None

    def get_number(self):
        """Seek the next number in input_file.

        Return the number (or None) and the next non-numeric character.
        """
        # find start of number
        while True:
            char = self.input_file.read(1)
            if char.isdigit():
                num = char
                break
            elif char == '':
                return None

        # find end of number
        while True:
            char = self.input_file.read(1)
            if char.isdigit():
                num = num+char
            else:
                return [num, char]
    
    def skip_spaces(self):
        """"advances until the character is no longer a space"""

        while self.current_character.isspace():

            if self.current_character == "\n":
                self.character_count = -1

            self.current_character = self.input_file.read(1)
            self.character_count += 1


    def advance(self):
        """reads one further character into the document"""

        char = self.input_file.read(1)
        self.current_character = char
        return char