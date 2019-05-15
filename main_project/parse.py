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

        # skip first N linebreaks
        self.scanner.skip_newline()

        while True:
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue

            if self.symbol.type == self.scanner.HEADING:
                #comment out whichever lines you want in order to debug your section
                if self.symbol.id == self.scanner.DEVICES_ID:
                    self.parse_section('devices')
                # elif self.symbol.id == self.scanner.INIT_ID:
                #     self.parse_section('init')
                # elif self.symbol.id == self.scanner.CONNECTION_ID:
                #     self.parse_section('connections')
                elif self.symbol.id == self.scanner.MONITOR_ID:
                    self.parse_section('monitor')
            
            elif self.symbol.type == self.scanner.NEW_LINE:
                continue

            elif self.symbol.type == self.scanner.EOF:
                break
            else:
                raise SyntaxError("not allowed to write symbol type {} outside of section".format(self.symbol.type))
                
        # Returns True if correctly parsed
        return True
    
    def parse_section(self, heading):
        """Parse 1 section block encapsulated by '{' and '}' and build circuit"""
        
        while True: # find opening curly bracket
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            elif self.symbol.type == self.scanner.NEW_LINE:
                continue
            elif self.symbol.type == self.scanner.CURLY_OPEN:
                break
            else:
                raise SyntaxError("Illegal character after heading title")

        if heading == 'devices':
            while self.parse_device():
                pass      

            # ----------- CHECK EVERYTHING IS SPECIFIED -------------- #
            for i in self.devices.devices_list:
                if i.inputs == {}:
                    raise UnboundLocalError("Gate has no input")
                if i.outputs == {}:
                    raise UnboundLocalError("Gate has no output")      

        elif heading == 'init':
            # call parse device() here to create switches
            pass
        elif heading == 'connections':
            # call connect() here to add the wiring
            pass
        elif heading == 'monitor':
            self.add_monitor_point()
            
        else:
            raise NameError('not valid heading name')

        # end of section
            
    def parse_device(self):
        """Build devices by reading 1 line at a time"""
        # ----------- CREATES DEVICES -------------- #
        # FORMAT = A, B are NAND gates
        # OR FORMAT = A1 => A12 are NAND gates

        definition_delimiters = [self.scanner.IS, self.scanner.ARE]
        attribute_delimiters = [self.scanner.HAS, self.scanner.HAVE]

        devices, definition = self.get_names_before_delimiter(definition_delimiters, attribute_delimiters)
        if definition is None:
            return False

        if definition:
            # -------------- GET GATE TYPE -------------- #
            self.symbol = self.scanner.get_symbol()
            word = self.scanner.names.get_name_string(self.symbol.id)
            if word in self.device_list:
                gate_type = self.devices.names.query(word)
            else:
                raise SyntaxError("Invalid gate type")

            for i in devices:
                # add gates to model
                self.devices.add_device(i, gate_type)
                self.devices.add_output(i, 0)
        
        else:
            # -------------- GET NUM INPUTS ------------- #
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.id[0])
                # print(devices)
                for device in devices:
                    if self.devices.get_device(device).device_kind == self.devices.names.query("NOT") and num > 1:
                        raise ValueError("Too many inputs for gate type")
                    for i in range(1, num+1):
                        self.devices.add_input(device, i)
            else:
                raise SyntaxError("Expected number")

        while True: # continue to end of line regardless
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            if self.symbol.type == self.scanner.NEW_LINE:
                break
        
        return True


    def parse_init(self):
        pass


    def parse_connections(self):
        pass
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
        while True:
            names, status = self.get_names_before_delimiter([],[])

            if status is None:
                break
        
        tmp = []
        for name in names:
            tmp.append(self.devices.get_signal_ids(name+".0"))

        return True


    def get_names_before_delimiter(self, true_delimiting_word_ids, false_delimiting_word_ids):
        """ tripwire function which takes 2 arrays of name_ids. Returns names and which list is encountered first"""

        devices = []
        list_format = ret_val = None
        while True:
            # get first SYMBOL
            self.symbol = self.scanner.get_symbol()
            if self.symbol == None: # ignore the word if ignorable
                continue
            
            elif self.symbol.type == self.scanner.CURLY_CLOSE:  # exit and parse
                return devices, None

            elif self.symbol.type == self.scanner.COMMA:
                list_format = True
                continue

            elif self.symbol.type == self.scanner.ARROW:    # if user specifies arrow notation
                if list_format:
                    raise SyntaxError
                list_format = False
                
                # find next name
                self.symbol = self.scanner.get_symbol()
                if self.symbol == None:
                    raise SyntaxError
                
                elif self.symbol.type == self.scanner.NAME:
                    word = self.scanner.names.get_name_string(self.symbol.id)
                    devices.append(word)
                    
                    if self.symbol.id in true_delimiting_word_ids:  # if definition
                        ret_val = True
                        break
                    if self.symbol.id in false_delimiting_word_ids: # if attribute
                        ret_val = False
                        break

            elif self.symbol.type == self.scanner.NAME:
                word = self.scanner.names.get_name_string(self.symbol.id)
                devices.append(word)
                
                if self.symbol.id in true_delimiting_word_ids:  # if definition
                    ret_val = True
                    break
                if self.symbol.id in false_delimiting_word_ids: # if attribute
                    ret_val = False
                    break


            if self.symbol.id in true_delimiting_word_ids:  # if definition
                ret_val = True
                break
            if self.symbol.id in false_delimiting_word_ids: # if attribute
                ret_val = False
                break

        if not list_format and len(devices) == 2:
            
            base = devices[0].rstrip('0123456789') # gets base string
            low = re.match('.*?([0-9]+)$', devices[0]).group(1)
            high = re.match('.*?([0-9]+)$', devices[1]).group(1)
            lowint, highint = int(low), int(high)

            if lowint > highint:
                raise ValueError("incorrect order of range values")
            
            devices = []
            for i in range(lowint, highint+1):
                devices.append(base+str(i))

        return devices, ret_val