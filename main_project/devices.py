"""Make devices and set device properties.

Used in the Logic Simulator project to make devices and ports and store their
properties.

Classes
-------
Device - stores device properties.
Devices - makes and stores all the devices in the logic network.
"""
import random


class Device:

    """Store device properties.

    Parameters
    ----------
    device_id: device ID.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, device_id):
        """Initialise device properties."""

        self.device_id = device_id

        # inputs dictionary stores
        # {input_id: (connected_output_device_id, connected_output_port_id)}
        self.inputs = {}

        # outputs dictionary stores {output_id: output_signal}
        self.outputs = {}

        self.device_kind = None
        self.clock_half_period = None
        self.clock_counter = None
        self.switch_state = None
        self.dtype_memory = None


class Devices:

    """Make and store devices.

    This class contains many functions for making devices and ports.
    It stores all the devices in a list.

    Parameters
    ----------
    names: instance of the names.Names() class.

    Public methods
    --------------
    get_device(self, device_id): Returns the Device object corresponding
                                 to the device ID.

    find_devices(self, device_kind=None): Returns a list of device_ids of
                                          the specified device_kind.

    add_device(self, device_id, device_kind): Adds the specified device to the
                                              network.

    add_input(self, device_id, input_id): Adds the specified input to the
                                          specified device.

    add_output(self, device_id, output_id, signal=0): Adds the specified output
                                                      to the specified device.

    get_signal_name(self, device_id, output_id): Returns the name string of the
                                                 specified signal.

    get_signal_ids(self, signal_name): Returns the device and output IDs of
                                       the specified signal.

    set_switch(self, device_id, signal): Sets switch_state of specified device
                                         to signal.

    make_switch(self, device_id, initial_state): Makes a switch device and sets
                                                 its initial state.

    make_clock(self, device_id, clock_half_period): Makes a clock device with
                                                    the specified half period.

    make_gate(self, device_id, device_kind, no_of_inputs): Makes logic gates
                                        with the specified number of inputs.

    make_d_type(self, device_id): Makes a D-type device.

    cold_startup(self): Simulates cold start-up of D-types and clocks.

    make_device(self, device_id, device_kind, device_property=None): Creates
                       the specified device and returns errors if unsuccessful.
    """

    def __init__(self, names):
        """Initialise devices list and constants."""

        self.names = names

        self.devices_list = []

        gate_strings = ["AND", "OR", "NAND", "NOR", "XOR"]
        device_strings = ["CLOCK", "SWITCH", "DTYPE"]
        dtype_inputs = ["CLK", "SET", "CLEAR", "DATA"]
        dtype_outputs = ["Q", "QBAR"]

        [self.NO_ERROR, self.INVALID_QUALIFIER, self.NO_QUALIFIER,
         self.BAD_DEVICE, self.QUALIFIER_PRESENT,
         self.DEVICE_PRESENT] = self.names.unique_error_codes(6)

        self.signal_types = [self.LOW, self.HIGH, self.RISING,
                             self.FALLING, self.BLANK] = range(5)
        self.gate_types = [self.AND, self.OR, self.NAND, self.NOR,
                           self.XOR] = self.names.lookup(gate_strings)
        self.device_types = [self.CLOCK, self.SWITCH,
                             self.D_TYPE] = self.names.lookup(device_strings)
        self.dtype_input_ids = [self.CLK_ID, self.SET_ID, self.CLEAR_ID,
                                self.DATA_ID] = self.names.lookup(dtype_inputs)
        self.dtype_output_ids = [
            self.Q_ID, self.QBAR_ID] = self.names.lookup(dtype_outputs)

        self.max_gate_inputs = 16

    def get_device(self, device_id):
        """Return the Device object corresponding to device_id."""
        for device in self.devices_list:
            if device.device_id == device_id:
                return device
        return None

    def find_devices(self, device_kind=None):
        """Return a list of device IDs of the specified device_kind.

        Return a list of all device IDs in the network if no device_kind is
        specified.
        """
        device_id_list = []
        for device in self.devices_list:
            if device_kind is None:
                device_id_list.append(device.device_id)
            elif device.device_kind == device_kind:
                device_id_list.append(device.device_id)
        return device_id_list

    def add_device(self, device_id, device_kind):
        """Add the specified device to the network."""
        new_device = Device(device_id)
        new_device.device_kind = device_kind
        self.devices_list.append(new_device)

    def add_input(self, device_id, input_id):
        """Add the specified input to the specified device.

        Return True if successful.
        """
        device = self.get_device(device_id)
        if device is not None:
            device.inputs.setdefault(input_id)
            return True
        else:
            return False

    def add_output(self, device_id, output_id, signal=0):
        """Add the specified output to the specified device.

        Return True if successful. The default output signal is LOW (0).
        """
        device = self.get_device(device_id)
        if device is not None:
            device.outputs[output_id] = signal
            return True
        else:
            return False

    def get_signal_name(self, device_id, port_id):
        """Return the name string of the specified signal.

        The signal is specified by its device_id and port_id. Return None if
        either ID is invalid.
        """
        device = self.get_device(device_id)
        if device is not None:
            device_name = self.names.get_name_string(device_id)
            if port_id is None:
                signal_name = device_name
                return signal_name
            elif port_id in device.outputs or port_id in device.inputs:
                port_name = self.names.get_name_string(port_id)
                signal_name = ".".join([device_name, port_name])
                return signal_name
            else:
                return None
        else:
            return None

    def get_signal_ids(self, signal_name):
        """Return the device and output IDs of the specified signal."""
        name_string_list = signal_name.split(".")
        name_id_list = self.names.lookup(name_string_list)
        device_id = name_id_list[0]
        if len(name_id_list) == 2:
            output_id = name_id_list[1]
        else:
            output_id = None

        return [device_id, output_id]

    def set_switch(self, device_id, signal):
        """Set the switch state of the specified device to signal.

        Return True if successful.
        """
        device = self.get_device(device_id)
        if device is None:
            return False
        elif device.device_kind != self.SWITCH:
            return False
        else:
            device.switch_state = signal
            return True

    def make_switch(self, device_id, initial_state):
        """Make a switch device and set its initial state."""
        self.add_device(device_id, self.SWITCH)
        self.add_output(device_id, output_id=None)
        self.set_switch(device_id, initial_state)

    def make_clock(self, device_id, clock_half_period):
        """Make a clock device with the specified half period.

        clock_half_period is an integer > 0. It is the number of simulation
        cycles before the clock switches state.
        """
        self.add_device(device_id, self.CLOCK)
        device = self.get_device(device_id)
        device.clock_half_period = clock_half_period
        self.cold_startup()  # clock initialised to a random point in its cycle

    def make_gate(self, device_id, device_kind, no_of_inputs):
        """Make logic gates with the specified number of inputs."""
        self.add_device(device_id, device_kind)
        self.add_output(device_id, output_id=None)

        for input_number in range(1, no_of_inputs + 1):
            input_name = "".join(["I", str(input_number)])
            [input_id] = self.names.lookup([input_name])
            self.add_input(device_id, input_id)

    def make_d_type(self, device_id):
        """Make a D-type device."""
        self.add_device(device_id, self.D_TYPE)
        for input_id in self.dtype_input_ids:
            self.add_input(device_id, input_id)
        for output_id in self.dtype_output_ids:
            self.add_output(device_id, output_id)
        self.cold_startup()  # D-type initialised to a random state

    def cold_startup(self):
        """Simulate cold start-up of D-types and clocks.

        Set the memory of the D-types to a random state and make the clocks
        begin from a random point in their cycles.
        """
        for device in self.devices_list:
            if device.device_kind == self.D_TYPE:
                device.dtype_memory = random.choice([self.LOW, self.HIGH])

            elif device.device_kind == self.CLOCK:
                clock_signal = random.choice([self.LOW, self.HIGH])
                self.add_output(device.device_id, output_id=None,
                                signal=clock_signal)
                # Initialise it to a random point in its cycle.
                device.clock_counter = \
                    random.randrange(device.clock_half_period)

    def make_device(self, device_id, device_kind, device_property=None):
        """Create the specified device.

        Return self.NO_ERROR if successful. Return corresponding error if not.
        """
        # Device has already been added to the devices_list
        if self.get_device(device_id) is not None:
            error_type = self.DEVICE_PRESENT

        elif device_kind == self.SWITCH:
            # Device property is the switch initial state: 0(LOW) or 1(HIGH)
            if device_property is None:
                error_type = self.NO_QUALIFIER
            elif device_property not in [self.LOW, self.HIGH]:
                error_type = self.INVALID_QUALIFIER
            else:
                self.make_switch(device_id, device_property)
                error_type = self.NO_ERROR

        elif device_kind == self.CLOCK:
            # Device property is the clock half period > 0
            if device_property is None:
                error_type = self.NO_QUALIFIER
            elif device_property <= 0:
                error_type = self.INVALID_QUALIFIER
            else:
                self.make_clock(device_id, device_property)
                error_type = self.NO_ERROR

        elif device_kind in self.gate_types:
            # Device property is the number of inputs
            if device_kind == self.XOR:
                if device_property is not None:
                    error_type = self.QUALIFIER_PRESENT
                else:
                    self.make_gate(device_id, device_kind, 2)
                    error_type = self.NO_ERROR
            else:  # other gates
                if device_property is None:
                    error_type = self.NO_QUALIFIER
                elif device_property not in range(1, 17):  # between 1 and 16
                    error_type = self.INVALID_QUALIFIER
                else:
                    self.make_gate(device_id, device_kind, device_property)
                    error_type = self.NO_ERROR

        elif device_kind == self.D_TYPE:
            if device_property is not None:
                error_type = self.QUALIFIER_PRESENT
            else:
                self.make_d_type(device_id)
                error_type = self.NO_ERROR

        else:
            error_type = self.BAD_DEVICE

        return error_type
