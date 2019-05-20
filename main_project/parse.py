import re
import sys
from error import SemanticError

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
                # comment out whichever lines you want in order to debug your section
                if self.symbol.id == self.scanner.DEVICES_ID:
                    self.parse_section('devices')
                elif self.symbol.id == self.scanner.INIT_ID:
                    self.parse_section('init')
                elif self.symbol.id == self.scanner.CONNECTION_ID:
                    self.parse_section('connections')
                elif self.symbol.id == self.scanner.MONITOR_ID:
                    self.parse_section('monitor')
                else:
                    self.error(SyntaxError, "Heading name '{}' not allowed".format(
                        self.scanner.name_string))

            elif self.symbol.type == self.scanner.NEW_LINE:
                continue

            elif self.symbol.type == self.scanner.EOF:
                break
            else:
                self.error(SyntaxError, "not allowed to write {} outside of section. Expected heading name".format(
                    self.scanner.name_string))

        # Returns True if correctly parsed
        return True

    def parse_section(self, heading):
        """Parse 1 section block encapsulated by '{' and '}' and build circuit"""

        while True:  # find opening curly bracket
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            elif self.symbol.type == self.scanner.NEW_LINE:
                continue
            elif self.symbol.type == self.scanner.CURLY_OPEN:
                break
            else:
                self.error(
                    SyntaxError, "Illegal character after heading title")

        if heading == 'devices':
            while self.parse_device():
                pass

            # ----------- CHECK DEVICE IS SPECIFIED ----------- #
            for i in self.devices.devices_list:

                if i.inputs == {}:
                    self.error(SemanticError,
                               "No inputs specified for gate '{}' ".format(i.device_id))
                if i.outputs == {}:
                    self.error(SemanticError,
                               "Gate '{}' has no output".format(i.device_id))

                print("[name: {}, type: {}, num_inputs: {}, num_outputs: {}]".format(i.device_id,
                                                                                     self.names.get_name_string(i.device_kind), i.inputs, i.outputs))

        elif heading == 'init':
            # call parse device() here to create switches
            no_curlies = self.parse_connections(self, 0)
            while no_curlies < 2:
                no_curlies = self.parse_connections(self, no_curlies)
            pass
        elif heading == 'connections':
            # call connect() here to add the wiring

            pass

        elif heading == 'monitor':
            while self.add_monitor_point():
                pass

        print("END OF SECTION")

    def parse_device(self):
        """Build devices by reading 1 line at a time"""
        # ----------- CREATES DEVICES -------------- #
        # FORMAT = A, B are NAND gates
        # OR FORMAT = A1 => A12 are NAND gates

        definition_delimiters = [self.scanner.IS, self.scanner.ARE]
        attribute_delimiters = [self.scanner.HAS, self.scanner.HAVE]

        devices, definition = self.get_names_before_delimiter(
            definition_delimiters, attribute_delimiters)
        if definition is None:
            if devices is None:
                # reached end of section
                return False
            else:
                pass

        if definition:
            # -------------- GET GATE TYPE -------------- #
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                self.error(SyntaxError, "English doesn't make sense")

            device_type = self.scanner.names.get_name_string(self.symbol.id)

            for name in devices:
                # add gates to model
                [i] = self.devices.names.lookup([name])

                if device_type is "DTYPE":
                    self.devices.make_d_type(i)

                elif device_type is "XOR":
                    self.devices.add_device(
                        i, self.devices.names.query(device_type))
                    self.devices.add_output(i, None)
                    [inp1, inp2] = self.devices.names.lookup([str(1), str(2)])
                    self.devices.add_input(i, inp1)
                    self.devices.add_input(i, inp2)

                elif device_type is "NOT":
                    self.devices.add_device(
                        i, self.devices.names.query(device_type))
                    self.devices.add_output(i, None)
                    [inp1] = self.devices.names.lookup([str(1)])
                    self.devices.add_input(i, inp1)

                # must be a gate - user must specify inputs
                elif device_type in ["AND", "NAND", "OR", "NOR"]:
                    self.devices.add_device(
                        i, self.devices.names.query(device_type))
                    self.devices.add_output(i, None)

                else:
                    self.error(
                        SyntaxError, "Can't create device {} in this section".format(device_type))

        else:
            # -------------- GET NUM INPUTS ------------- #
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.id[0])

                for device in devices:
                    ID = self.devices.names.query(device)

                    # TODO: Add proper error catching method
                    if self.devices.get_device(ID) is None:
                        self.error(SemanticError,
                                   "Device '{}' does not exist".format(device))

                    elif self.devices.get_device(ID).device_kind == self.devices.names.query("DTYPE"):
                        self.error(
                            SemanticError, "Not allowed to specify inputs for a DTYPE device")

                    elif self.devices.get_device(ID).device_kind == self.devices.names.query("XOR"):
                        if num != 2:
                            self.error(SemanticError,
                                       "XOR gate must have 2 inputs")

                    elif self.devices.get_device(ID).device_kind == self.devices.names.query("NOT"):
                        if num >= 2:
                            self.error(SemanticError,
                                       "Too many inputs for NOT gate")

                    else:
                        if num > 16:
                            self.error(SemanticError,
                                       "max inputs allowed is 16")
                        else:
                            for i in range(1, num+1):
                                [inp_id] = self.devices.names.lookup([str(i)])
                                if self.devices.add_input(ID, inp_id):
                                    pass
                                else:
                                    self.error(SemanticError,
                                               "Adding input failure")

            else:
                self.error(SyntaxError, "Expected number")

        while True:  # continue to end of line or } CAREFUL!!
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            elif self.symbol.type == self.scanner.NEW_LINE:
                return True
            elif self.symbol.type == self.scanner.CURLY_CLOSE:
                return False
            # else:
            #     print(self.symbol.type)
            #     print(self.scanner.name_string)
            #     self.error(SyntaxError, "Unexpected symbol encountered while parsing")

    def parse_init(self):
        """Build inits by reading 1 line at a time"""
        # ----------- CREATES INITIALISERS -------------- #
        # FORMAT = A, B are SWITCHES
        # OR FORMAT = A1 => A12 are SWITCHES

        definition_delimiters = [self.scanner.IS, self.scanner.ARE]
        attribute_delimiters = [self.scanner.HAS, self.scanner.HAVE]

        devices, definition = self.get_names_before_delimiter(
            definition_delimiters, attribute_delimiters)
        if definition is None:
            if devices is None:
                # reached end of section
                return False
            else:
                pass

        if definition:
            # -------------- GET INIT TYPE -------------- #
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                self.error(SyntaxError, "English doesn't make sense")

            init_type = self.scanner.names.get_name_string(self.symbol.id)

            for name in devices:
                # add init to model
                [i] = self.devices.names.lookup([name])

                if init_type is "SWITCH":
                    self.devices.make_switch(i,device)

                elif device_type is "CLOCK":
                    self.devices.add_device(
                        i, self.devices.names.query(device_type))
                    self.devices.add_output(i, None)
                    [inp1, inp2] = self.devices.names.lookup([str(1), str(2)])
                    self.devices.add_input(i, inp1)
                    self.devices.add_input(i, inp2)

                else:
                    self.error(
                        SyntaxError, "Can't create device {} in this section".format(device_type))

        else:
            # -------------- GET NUM INPUTS ------------- #
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NUMBER:
                num = int(self.symbol.id[0])

                for device in devices:
                    ID = self.devices.names.query(device)

                    # TODO: Add proper error catching method
                    if self.devices.get_device(ID) is None:
                        self.error(SemanticError,
                                   "Device '{}' does not exist".format(device))

                    elif self.devices.get_device(ID).device_kind == self.devices.names.query("DTYPE"):
                        self.error(
                            SemanticError, "Not allowed to specify inputs for a DTYPE device")

                    elif self.devices.get_device(ID).device_kind == self.devices.names.query("XOR"):
                        if num != 2:
                            self.error(SemanticError,
                                       "XOR gate must have 2 inputs")

                    elif self.devices.get_device(ID).device_kind == self.devices.names.query("NOT"):
                        if num >= 2:
                            self.error(SemanticError,
                                       "Too many inputs for NOT gate")

                    else:
                        if num > 16:
                            self.error(SemanticError,
                                       "max inputs allowed is 16")

                        for i in range(1, num + 1):
                            [inp_id] = self.devices.names.lookup([str(i)])
                            if self.devices.add_input(ID, inp_id):
                                pass
                            else:
                                self.error(SemanticError,
                                           "Adding input failure")

            else:
                self.error(SyntaxError, "Expected number")

        while True:  # continue to end of line or } CAREFUL!!
            self.symbol = self.scanner.get_symbol()
            if self.symbol is None:
                continue
            elif self.symbol.type == self.scanner.NEW_LINE:
                return True
            elif self.symbol.type == self.scanner.CURLY_CLOSE:
                return False
            # else:
            #     print(self.symbol.type)
            #     print(self.scanner.name_string)
            #     self.error(SyntaxError, "Unexpected symbol encountered while parsing")

    def parse_connections(self, curlies): #doesn't delimit by device, as some devices will have BARs and so it makes more sense to go line by line

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.CURLY_CLOSE:
            curlies += 1
            return curlies

        if self.symbol.id != self.scanner.DEVICES_ID: #checks if first word is "Device"
            self.error(SyntaxError, "First word is not Device")
        else:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.NAME: #checks is the second word is a name
                self.error(SemanticError, "'{}' is not a name".format(self.symbol))
            else:
                device = self.devices.get_device(self.symbol.id)
                DEVICE_INPUT = device
                if device is Nome: #checks if second word is a valid device
                    self.error(SyntaxError, "A device with this name does not exist")
                else:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type != self.scanner.CURLY_OPEN:
                        self.error(SyntaxError, "After detailing the device, a curly bracket is required")
                    else:
                        pass

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.NAME:
            pass
        else:
            self.error(SemanticError, "You must have a name at the start of the connection and '{}' is not a name".format(self.symbol))

        first_device = self.devices.get_device(self.symbol.id)
        if first_device is None:
            self.error(SyntaxError, "A device with the name at the start of the connection does not exist")


        if first_device.device_kind() == self.devices.D_TYPE:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.DOT:
                self.error(SyntaxError, "There should be a dot after the name of a DTYPE device")
            self.symbol = self.scanner.get_symbol()
            if self.symbol not in self.devices.dtype_output_ids:
                self.error(SemanticError, "This is an invalid output type for a DTYPE")
            first_device_output_id = self.symbol.id
        else:
            first_device_output_id = None

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.TO:
            print("there should be a 'to' after the first device")
            self.error(SyntaxError, "Please add the word 'to' between your connection points!")

        self.symbol = self.scanner.get_symbol()
        end_device = self.devices.get_device(self.symbol.id) #finds device at end of "wire"

        if end_device is None:
            self.error(SemanticError, "No such device exists at the end of the connection")

        if end_device != DEVICE_INPUT:
            self.error(SyntaxError, "Device name at end of connection does not fit with section device name")


        self.symbol = self.scanner.get_symbol() #finds next symbol, should be a dot
        if self.symbol.type != self.scanner.DOT:
            self.error(SyntaxError, "There should be a dot between the end device name and the port number/name")


        self.symbol = self.scanner.get_symbol() # finds port number

        if self.symbol.type != self.scanner.NAME:
            self.error(SyntaxError, "There should be a port name for the end of the connection")


        second_device_input_id = self.symbol.id


        if DEVICE_INPUT.device_kind == self.devices.D_TYPE:
            pass

        self.network.make_connection(self, DEVICE_INPUT.id, first_device_output_id, end_device.id, second_device_input_id)
        return 0

        #check if port number is valid

        #check if device has that many port numbers - there doesn't seem to be a method in devices for doing this, I could test for DTYPE and XOR but it should work for all of them
        # however, the make_connections function in network already does a lot of this

        """if end_device_type == "DTYPE":
            if port_no not in dtpye_ports:
                print("That's not a DTPYE port")
        else:
            if type(port_no) != int:
                print("port number has to be an integer")
        if end_device_type == "XOR":
            if port_no > 2:
                print("XOR gates can only have 2 input ports")

        if port_no not in end_device_type.inputs[end_device]:
            return("port number is not in end device inputs")

        if has_not == 0:
            self.network.make_connection(self, actual_device, actual_device, end_device, port_no)
        else:
            self.network.make_connection(self, actual_device, first_device, end_device, port_no)"""









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

        self.symbol = self.scanner.get_symbol(query=True)
        if self.symbol.type == self.scanner.CURLY_CLOSE:
            return False
        if self.symbol.type in [self.scanner.COMMA, self.scanner.NEW_LINE]:
            return True

        elif self.symbol.type == self.scanner.NAME:

            status = self.monitors.make_monitor(
                self.symbol.id, None)

            if status == self.monitors.network.DEVICE_ABSENT:
                self.error(SemanticError, "Device '{}' doesn't exist".format(
                    self.scanner.name_string))
            elif status == self.monitors.NOT_OUTPUT:
                self.error(SemanticError, "Name '{}' is not an output".format(
                    self.scanner.name_string))
            elif status == self.monitors.MONITOR_PRESENT:
                self.error(SemanticError, "Already monitoring {}".format(
                    self.scanner.name_string))
            elif status == self.monitors.NO_ERROR:
                pass

        return True

    def get_names_before_delimiter(self, true_delimiting_word_ids, false_delimiting_word_ids):
        """ 
        Tripwire function which takes 2 arrays of name_ids.
        Params: 2 lists containing word IDs

        Returns [list of device name strings ,  which array is tripped (True, False or Error)]
        """

        devices = []
        list_format = ret_val = name_found = None
        while True:
            # ------------ GET FIRST SYMBOL ------------ #
            self.symbol = self.scanner.get_symbol()
            if self.symbol == None:  # ignore the word if ignorable
                continue

            elif self.symbol.type == self.scanner.CURLY_CLOSE:  # error in parsing
                if name_found:
                    self.error(
                        SyntaxError, "} encountered, couldn't parse")
                else:
                    return None, None  # if curly bracket on line, end is reached

            elif self.symbol.type == self.scanner.NEW_LINE:  # trim leading linebreaks
                if name_found:
                    self.error(SyntaxError, "end of line, coundn't parse")
                else:
                    continue

            elif self.symbol.type == self.scanner.NAME:
                name_found = True   # checks word has been found
                word = self.scanner.names.get_name_string(self.symbol.id)
                devices.append(word)

                if self.symbol.id in true_delimiting_word_ids:  # if definition
                    ret_val = True
                    break
                elif self.symbol.id in false_delimiting_word_ids:  # if attribute
                    ret_val = False
                    break

            elif self.symbol.type == self.scanner.COMMA:
                list_format = True
                continue

            elif self.symbol.type == self.scanner.ARROW:    # if user specifies arrow notation
                # ------- USER SPECIFIED RANGE NOTATION -------- #
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
                    elif self.symbol.id in false_delimiting_word_ids:  # if attribute
                        ret_val = False
                        break

            if self.symbol.id in true_delimiting_word_ids:  # if definition
                ret_val = True
                break
            elif self.symbol.id in false_delimiting_word_ids:  # if attribute
                ret_val = False
                break

        # -------- RANGE NOTATION -------- #
        if list_format == False:
            if len(devices) is 2:
                base = devices[0].rstrip('0123456789')  # gets base string
                if devices[1].rstrip('0123456789') != base:
                    self.error(SyntaxError, "Name bases are inconsistent, '{}' and '{}'".format(
                        base, devices[1].rstrip('0123456789')))  # gets base string

                low = re.match('.*?([0-9]+)$', devices[0]).group(1)
                high = re.match('.*?([0-9]+)$', devices[1]).group(1)
                lowint, highint = int(low), int(high)

                if lowint > highint:
                    self.error(ValueError, "incorrect order of range values")

                devices = []
                for i in range(lowint, highint+1):
                    devices.append(base+str(i))
            else:
                raise self.error(
                    SyntaxError, "Devices length must be 2 when using => notation")

        return devices, ret_val

    def error(self, error_type, message=""):
        self.scanner.error(error_type, message)
