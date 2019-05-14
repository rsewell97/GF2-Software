#!/usr/bin/env python3
import sys
"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""

        self.scanner = scanner
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        self.symbol_type = None
        self.symbol_id = None
        self.error_counter = 0

        [self.NO_DEVICE_KEYWORD, self.NO_CONNECTIONS_KEYWORD,
         self.NO_MONITOR_KEYWORD, self.MISSING_COLON, self.MISSING_SEMICOLON,
         self.INVALID_DEVICE_NAME, self.MISSING_DELIMITER, self.PORT_MISSING,
         self.INVALID_OUTPUT, self.INVALID_INPUT, self.MISSING_ARROW,
         self.NOT_ALL_INPUTS_CONNECTED, self.UNEXPECTED_SYMBOL,
         self.PREMATURE_EOF, self.COMMA_NOT_SEMICOLON,
         self.CONNECTIONS_DUPLICATE
         ] = self.names.unique_error_codes(16)

        self.device_list = ["DTYPE", "XOR", "AND", "NAND", "OR", "NOR",
                            "SWITCH", "CLOCK", "RC", "NOT"]
        self.type_id_list = self.names.lookup(self.device_list)
    
    def parse_network(self):
        """Parse the circuit definition file."""

        self.scanner.skip_newline()
        # skip first N linebreaks

        while True:
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue

            if self.symbol.type == self.scanner.HEADING:

                if self.symbol.id == self.scanner.DEVICES_ID:
                    self.parse_section(self.scanner.DEVICES_ID)
                    # sys.exit()
                # elif self.symbol.id == self.scanner.INPUTS_ID:
                #     self.parse_section()
                # elif self.symbol.id == self.scanner.CONNECTION_ID:
                #     self.parse_section()
                # elif self.symbol.id == self.scanner.MONITOR_ID:
                #     self.parse_section()
            # else:
            #     print(self.scanner.current_character)
            #     raise SyntaxError("not allowed to write lines outside of keywords")

            if self.symbol.type == self.scanner.EOF:
                break

        print(self.devices.devices_list)
    
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
    
    def parse_section(self, heading_id):
        """Parse 1 section block encapsulated by '{' and '}' and build circuit"""
        while True:
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            elif self.symbol.type == self.scanner.CURLY_OPEN:
                break
            else:
                raise SyntaxError("Illegal character after heading title")
        
        nest_count = 1 # layers of curly brackets
        while nest_count > 0: #loops 1 line at a time by calling parse_device()
            
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None: # ignore the word
                continue
            
            if self.symbol.type == self.scanner.CURLY_OPEN:
                nest_count += 1
            elif self.symbol.type == self.scanner.CURLY_CLOSE:
                nest_count -= 1
    
            else:
                self.parse_device()

            if nest_count < 1: # end of section
                break

        # end of section
            
    def parse_device(self):
        """Build devices by reading 1 line at a time"""
        # print(self.scanner.current_character)
        # while self.scanner.current_character != self.scanner.NEW_LINE:

        #     self.symbol = self.scanner.get_symbol()
        #     if self.symbol.type == self.scanner.NAME:
        #         print("")
        pass