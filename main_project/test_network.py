"""Test the network module."""
import pytest

from names import Names
from devices import Devices
from network import Network


@pytest.fixture
def new_network():
    """Return a new instance of the Network class."""
    new_names = Names()
    new_devices = Devices(new_names)
    return Network(new_names, new_devices)


@pytest.fixture
def network_with_devices():
    """Return a Network class instance with three devices in the network."""
    new_names = Names()
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)

    [SW1_ID, SW2_ID, OR1_ID] = new_names.lookup(["Sw1", "Sw2", "Or1"])

    # Add devices
    new_devices.make_device(SW1_ID, new_devices.SWITCH, 0)
    new_devices.make_device(SW2_ID, new_devices.SWITCH, 0)
    new_devices.make_device(OR1_ID, new_devices.OR, 2)

    return new_network


def test_get_connected_output(network_with_devices):
    """Test if the output connected to a given input port is correct."""
    network = network_with_devices
    devices = network.devices
    names = devices.names

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1", "I1",
                                                     "I2"])
    # Inputs are unconnected, get_connected_output should return None
    assert network.get_connected_output(OR1_ID, I1) is None
    assert network.get_connected_output(OR1_ID, I2) is None

    # Make connections
    network.make_connection(SW1_ID, None, OR1_ID, I1)
    network.make_connection(SW2_ID, None, OR1_ID, I2)

    assert network.get_connected_output(OR1_ID, I1) == (SW1_ID, None)
    assert network.get_connected_output(OR1_ID, I2) == (SW2_ID, None)

    # Not a valid port for Sw1, get_connected_output should return None
    assert network.get_connected_output(SW1_ID, I2) is None


def test_get_input_signal(network_with_devices):
    """Test if the signal at a given input port is correct"""
    network = network_with_devices
    devices = network.devices
    names = devices.names

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1", "I1",
                                                     "I2"])
    # Inputs are unconnected, get_input_signal should return None
    assert network.get_input_signal(OR1_ID, I1) is None
    assert network.get_input_signal(OR1_ID, I2) is None

    # Make connections
    network.make_connection(SW1_ID, None, OR1_ID, I1)
    network.make_connection(SW2_ID, None, OR1_ID, I2)

    # Set Sw2 output to HIGH
    switch2 = devices.get_device(SW2_ID)
    switch2.outputs[None] = devices.HIGH

    assert network.get_input_signal(OR1_ID, I1) == devices.LOW
    assert network.get_input_signal(OR1_ID, I2) == devices.HIGH


def test_get_output_signal(network_with_devices):
    """Test if the signal level at the given output is correct."""
    network = network_with_devices
    devices = network.devices
    names = devices.names

    [OR1_ID] = names.lookup(["Or1"])

    assert network.get_output_signal(OR1_ID, None) == devices.LOW

    # Set Or1 output to HIGH
    or1 = devices.get_device(OR1_ID)
    or1.outputs[None] = devices.HIGH

    assert network.get_output_signal(OR1_ID, None) == devices.HIGH


def test_check_network(network_with_devices):
    """Test if the signal at a given input port is correct."""
    network = network_with_devices
    devices = network.devices
    names = devices.names

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1", "I1",
                                                     "I2"])

    # Inputs are unconnected, check_network() should return False
    assert not network.check_network()

    # Make connections
    network.make_connection(SW1_ID, None, OR1_ID, I1)
    network.make_connection(SW2_ID, None, OR1_ID, I2)

    # Inputs are now connected, check_network() should return True
    assert network.check_network()


def test_make_connection(network_with_devices):
    """Test if the make_connection function correctly connects devices."""
    network = network_with_devices
    devices = network.devices
    names = devices.names

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1", "I1",
                                                     "I2"])

    or1 = devices.get_device(OR1_ID)

    # or1 inputs are initially unconnected
    assert or1.inputs == {I1: None,
                          I2: None}

    # Make connections
    network.make_connection(SW1_ID, None, OR1_ID, I1)
    network.make_connection(SW2_ID, None, OR1_ID, I2)

    # or1 inputs should now be connected
    assert or1.inputs == {I1: (SW1_ID, None),
                          I2: (SW2_ID, None)}


@pytest.mark.parametrize("function_args, error", [
    # I1 is not a valid device id
    ("(I1, I1, OR1_ID, I2)", "network.DEVICE_ABSENT"),

    ("(OR1_ID, I2, OR1_ID, I2)", "network.INPUT_TO_INPUT"),

    ("(SW1_ID, None, OR1_ID, None)", "network.OUTPUT_TO_OUTPUT"),

    # Switch device does not have port I1, so give PORT_ABSENT_ERROR
    ("(SW1_ID, I1, OR1_ID, I2)", "network.PORT_ABSENT"),

    # Output first
    ("(SW2_ID, None, OR1_ID, I2)", "network.NO_ERROR"),

    # Input first
    ("(OR1_ID, I2, SW2_ID, None)", "network.NO_ERROR"),

    # Note: Or1.I1 will have been connected earlier in the function
    ("(SW1_ID, None, OR1_ID, I1)", "network.INPUT_CONNECTED"),
])
def test_make_connection_gives_error(network_with_devices,
                                     function_args, error):
    """Test if the make_connection function returns the correct errors."""
    network = network_with_devices
    devices = network.devices
    names = devices.names

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1", "I1",
                                                     "I2"])

    # Connect Or1.I1 to Sw1
    network.make_connection(SW1_ID, None, OR1_ID, I1)

    # left_expression is of the form: network.make_connection(...)
    left_expression = eval("".join(["network.make_connection", function_args]))
    right_expression = eval(error)
    assert left_expression == right_expression


def test_execute_xor(new_network):
    """Test if execute_network returns the correct output for XOR gates."""
    network = new_network
    devices = network.devices
    names = devices.names

    [SW1_ID, SW2_ID, XOR1_ID, I1, I2] = names.lookup(
        ["Sw1", "Sw2", "Xor1", "I1", "I2"])

    # Make devices
    devices.make_device(XOR1_ID, devices.XOR)
    devices.make_device(SW1_ID, devices.SWITCH, 0)
    devices.make_device(SW2_ID, devices.SWITCH, 0)

    # Make connections
    network.make_connection(SW1_ID, None, XOR1_ID, I1)
    network.make_connection(SW2_ID, None, XOR1_ID, I2)

    network.execute_network()
    assert new_network.get_output_signal(XOR1_ID, None) == devices.LOW

    # Set Sw1 to HIGH
    devices.set_switch(SW1_ID, devices.HIGH)
    network.execute_network()
    assert network.get_output_signal(XOR1_ID, None) == devices.HIGH

    # Set Sw2 to HIGH
    devices.set_switch(SW2_ID, devices.HIGH)
    network.execute_network()
    assert network.get_output_signal(XOR1_ID, None) == devices.LOW


@pytest.mark.parametrize("gate_id, switch_outputs, gate_output, gate_kind", [
    ("AND1_ID", ["LOW", "HIGH", "LOW"], "LOW", "devices.AND"),
    ("AND1_ID", ["HIGH", "HIGH", "HIGH"], "HIGH", "devices.AND"),
    ("NAND1_ID", ["HIGH", "HIGH", "HIGH"], "LOW", "devices.NAND"),
    ("NAND1_ID", ["HIGH", "HIGH", "LOW"], "HIGH", "devices.NAND"),
    ("OR1_ID", ["LOW", "LOW", "LOW"], "LOW", "devices.OR"),
    ("OR1_ID", ["LOW", "HIGH", "HIGH"], "HIGH", "devices.OR"),
    ("NOR1_ID", ["HIGH", "LOW", "HIGH"], "LOW", "devices.NOR"),
    ("NOR1_ID", ["LOW", "LOW", "LOW"], "HIGH", "devices.NOR"),
])
def test_execute_non_xor_gates(new_network, gate_id, switch_outputs,
                               gate_output, gate_kind):
    """Test if execute_network returns the correct output for non-XOR gates."""
    network = new_network
    devices = network.devices
    names = devices.names

    [AND1_ID, OR1_ID, NAND1_ID, NOR1_ID, SW1_ID, SW2_ID, SW3_ID, I1, I2,
     I3] = names.lookup(["And1", "Or1", "Nand1", "Nor1", "Sw1", "Sw2", "Sw3",
                         "I1", "I2", "I3"])

    LOW = devices.LOW
    HIGH = devices.HIGH

    # Make devices
    gate_id = eval(gate_id)
    gate_kind = eval(gate_kind)
    devices.make_device(gate_id, gate_kind, 3)
    devices.make_device(SW1_ID, devices.SWITCH, 0)
    devices.make_device(SW2_ID, devices.SWITCH, 0)
    devices.make_device(SW3_ID, devices.SWITCH, 0)

    # Make connections
    network.make_connection(SW1_ID, None, gate_id, I1)
    network.make_connection(SW2_ID, None, gate_id, I2)
    network.make_connection(SW3_ID, None, gate_id, I3)

    # Set switches
    switches = [SW1_ID, SW2_ID, SW3_ID]
    for i, switch_output in enumerate(switch_outputs):
        devices.set_switch(switches[i], eval(switch_output))

    network.execute_network()
    assert network.get_output_signal(gate_id, None) == eval(gate_output)


def test_execute_non_gates(new_network):
    """Test if execute_network returns the correct output for non-gate devices.

    Tests switches, D-types and clocks.
    """
    network = new_network
    devices = network.devices
    names = devices.names

    LOW = devices.LOW
    HIGH = devices.HIGH

    # Make different devices
    [SW1_ID, SW2_ID, SW3_ID, CL_ID, D_ID] = names.lookup(["Sw1", "Sw2", "Sw3",
                                                          "Clock1", "D1"])
    devices.make_device(SW1_ID, devices.SWITCH, 1)
    devices.make_device(SW2_ID, devices.SWITCH, 0)
    devices.make_device(SW3_ID, devices.SWITCH, 0)
    devices.make_device(CL_ID, devices.CLOCK, 1)
    devices.make_device(D_ID, devices.D_TYPE)

    # Make connections
    network.make_connection(SW1_ID, None, D_ID, devices.DATA_ID)
    network.make_connection(CL_ID, None, D_ID, devices.CLK_ID)
    network.make_connection(SW2_ID, None, D_ID, devices.SET_ID)
    network.make_connection(SW3_ID, None, D_ID, devices.CLEAR_ID)

    # Get device outputs, the expression is in a string here so that it
    # can be re-evaluated again after executing devices
    sw1_output = "network.get_output_signal(SW1_ID, None)"
    sw2_output = "network.get_output_signal(SW2_ID, None)"
    sw3_output = "network.get_output_signal(SW3_ID, None)"
    clock_output = "network.get_output_signal(CL_ID, None)"
    dtype_Q = "network.get_output_signal(D_ID, devices.Q_ID)"
    dtype_QBAR = "network.get_output_signal(D_ID, devices.QBAR_ID)"

    # Execute devices until the clock is LOW at the start of its
    # period
    clock_device = devices.get_device(CL_ID)
    network.execute_network()
    while clock_device.clock_counter != 1 or eval(clock_output) != LOW:
        network.execute_network()

    # The clock is not rising yet, Q could be (randomly) HIGH or LOW
    assert [eval(sw1_output), eval(sw2_output), eval(sw3_output),
            eval(clock_output)] == [HIGH, LOW, LOW, LOW]

    assert eval(dtype_Q) in [HIGH, LOW]
    assert eval(dtype_QBAR) == network.invert_signal(eval(dtype_Q))

    network.execute_network()  # the clock has risen
    # While sw1(DATA) is high, Q has now changed to HIGH
    assert [eval(sw1_output), eval(sw2_output), eval(sw3_output),
            eval(clock_output), eval(dtype_Q), eval(dtype_QBAR)] == [
                HIGH, LOW, LOW, HIGH, HIGH, LOW]

    devices.set_switch(SW1_ID, LOW)  # Sw1 is connected to DATA
    devices.set_switch(SW2_ID, HIGH)  # Sw2 is connected to SET
    network.execute_network()  # the clock is not rising yet
    network.execute_network()  # the clock has risen
    # Even if sw1(DATA) is LOW, and the clock is rising,
    # sw2(SET) is HIGH, so Q is HIGH
    assert [eval(sw1_output), eval(sw2_output), eval(sw3_output),
            eval(clock_output), eval(dtype_Q), eval(dtype_QBAR)] == [
                LOW, HIGH, LOW, HIGH, HIGH, LOW]

    devices.set_switch(SW1_ID, HIGH)  # Sw1 is connected to DATA
    devices.set_switch(SW2_ID, LOW)  # Sw2 is connected to SET
    devices.set_switch(SW3_ID, HIGH)  # Sw3 is connected to CLEAR
    network.execute_network()  # the clock is not rising yet
    network.execute_network()  # the clock has risen
    # Even if sw1(DATA) is HIGH, and the clock is rising,
    # sw3(CLEAR) is HIGH, so Q is LOW
    assert [eval(sw1_output), eval(sw2_output), eval(sw3_output),
            eval(clock_output), eval(dtype_Q), eval(dtype_QBAR)] == [
                HIGH, LOW, HIGH, HIGH, LOW, HIGH]


def test_oscillating_network(new_network):
    """Test if the execute_network returns False for oscillating networks."""
    network = new_network
    devices = network.devices
    names = devices.names

    [NOR1, I1] = names.lookup(["Nor1", "I1"])
    # Make NOR gate
    devices.make_device(NOR1, devices.NOR, 1)

    # Connect the NOR gate to itself
    network.make_connection(NOR1, None, NOR1, I1)

    assert not network.execute_network()
