import sys
import re
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
                    self.parse_section('devices')
                    sys.exit()
                # elif self.symbol.id == self.scanner.INIT_ID:
                #     self.parse_section('init')
                # elif self.symbol.id == self.scanner.CONNECTION_ID:
                #     self.parse_section('connections')
                # elif self.symbol.id == self.scanner.MONITOR_ID:
                #     self.parse_section('monitor')
            
            elif self.symbol.type == self.scanner.EOF:
                break

            else:
                print(self.symbol.type)
                raise SyntaxError("not allowed to write lines outside of keywords")
            
            self.scanner.skip_newline()

        print(self.devices.devices_list)
    
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
    
    def parse_section(self, heading):
        """Parse 1 section block encapsulated by '{' and '}' and build circuit"""
        
        while True: # find opening curly bracket
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            elif self.symbol.type == self.scanner.CURLY_OPEN:
                break
            else:
                raise SyntaxError("Illegal character after heading title")

        if heading == 'devices':
            # call parse_device() here to create devices
            self.parse_device()

        elif heading == 'init':
            # call parse device() here to create switches
            pass
        elif heading == 'connections':
            # call connect() here to add the wiring
            pass
        elif heading == 'monitor':
            # call add_monitor_point() here
            pass
        else:
            raise NameError('not valid heading name')

        # end of section
            
    def parse_device(self):
        """Build devices by reading 1 line at a time"""

        # ----------- CREATES DEVICES --------------
        # FORMAT = A, B are NAND gates
        # OR FORMAT = A1 => A12 are NAND gates
        self.scanner.skip_newline() 

        devices = []
        list_format = None
        while True:
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            
            elif self.symbol.type == self.scanner.NEW_LINE:
                break

            elif self.symbol.type == self.scanner.COMMA:
                if list_format == False:
                    raise SyntaxError("cannot have , and => formats on 1 line")
                list_format = True
            elif self.symbol.type == self.scanner.ARROW:
                if list_format == True:
                    raise SyntaxError("cannot have , and => formats on 1 line")
                list_format = False

            elif self.symbol.type == self.scanner.NAME:
                word = self.scanner.names.get_name_string(self.symbol.id)

                if word in self.device_list:
                    gate_type = self.devices.names.query(word)
                else:
                    devices.append(word)

        if not list_format and len(devices) == 2:
            
            base = devices[0].rstrip('0123456789') # gets base string
            low = re.match('.*?([0-9]+)$', devices[0]).group(1)
            high = re.match('.*?([0-9]+)$', devices[1]).group(1)
            lowint, highint = int(low), int(high)

            if lowint > highint:
                raise ValueError("incorrect order of range values")
            for i in range(lowint, highint+1):
                self.devices.add_device(base+str(i), gate_type)

        else:
            for i in devices:
                self.devices.add_device(i, gate_type)

        print(len(self.devices.devices_list))


    def connect(self):
    
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.NAME:
            # must be an output
            id1 = self.symbol.id
        else:
            raise SyntaxError
        
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.TO:
            id1 = self.symbol.id
        elif self.symbol.type == self.scanner.DOT:
            raise IOError("input cannot be connected to another input")
        else:
            raise SyntaxError("Expected => symbol")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.NAME:
            id2 = self.symbol.id
        else:
            raise SyntaxError("must be in form device.input_number")
        
        # join id1, id2 - also check they existS

        # nest_count = 1 # tracks layers of curly brackets
        # while nest_count > 0: #loops 1 line at a time by calling parse_device()

        #     self.symbol = self.scanner.get_symbol()
        #     if self.symbol is None: # ignored the current symbol
        #         continue
            
        #     if self.symbol.type == self.scanner.CURLY_OPEN:
        #         nest_count += 1
        #     elif self.symbol.type == self.scanner.CURLY_CLOSE:
        #         nest_count -= 1
        #     else:
        #         self.parse_device()

        #     if nest_count < 1: # end of section
        #         break
        #     elif nest_count > max_nest:
        #         raise SyntaxError("unexpected token '{'")


    def add_monitor_point(self):
        pass
