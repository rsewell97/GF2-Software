"""Test the devices module."""
import pytest

from names import Names
from devices import Devices


@pytest.fixture
def new_devices():
    """Return a new instance of the Devices class."""
    new_names = Names()
    return Devices(new_names)


@pytest.fixture
def devices_with_items():
    """Return a Devices class instance with three devices in the network."""
    new_names = Names()
    new_devices = Devices(new_names)

    [AND1_ID, NOR1_ID, SW1_ID] = new_names.lookup(["And1", "Nor1", "Sw1"])

    new_devices.make_device(AND1_ID, new_devices.AND, 2)
    new_devices.make_device(NOR1_ID, new_devices.NOR, 16)
    new_devices.make_device(SW1_ID, new_devices.SWITCH, 0)

    return new_devices


def test_get_device(devices_with_items):
    """Test if get_device returns the correct device."""
    names = devices_with_items.names
    for device in devices_with_items.devices_list:
        assert devices_with_items.get_device(device.device_id) == device

        # get_device should return None for non-device IDs
        [X_ID] = names.lookup(["Random_non_device"])
        assert devices_with_items.get_device(X_ID) is None


def test_find_devices(devices_with_items):
    """Test if find_devices returns the correct devices of the given kind."""
    devices = devices_with_items
    names = devices.names
    device_names = [AND1_ID, NOR1_ID, SW1_ID] = names.lookup(["And1", "Nor1",
                                                              "Sw1"])

    assert devices.find_devices() == device_names
    assert devices.find_devices(devices.AND) == [AND1_ID]
    assert devices.find_devices(devices.NOR) == [NOR1_ID]
    assert devices.find_devices(devices.SWITCH) == [SW1_ID]
    assert devices.find_devices(devices.XOR) == []


def test_make_device(new_devices):
    """Test if make_device correctly makes devices with their properties."""
    names = new_devices.names

    [NAND1_ID, CLOCK1_ID, D1_ID, I1_ID,
     I2_ID] = names.lookup(["Nand1", "Clock1", "D1", "I1", "I2"])
    new_devices.make_device(NAND1_ID, new_devices.NAND, 2)  # 2-input NAND
    # Clock half period is 5
    new_devices.make_device(CLOCK1_ID, new_devices.CLOCK, 5)
    new_devices.make_device(D1_ID, new_devices.D_TYPE)

    nand_device = new_devices.get_device(NAND1_ID)
    clock_device = new_devices.get_device(CLOCK1_ID)
    dtype_device = new_devices.get_device(D1_ID)

    assert nand_device.inputs == {I1_ID: None, I2_ID: None}
    assert clock_device.inputs == {}
    assert dtype_device.inputs == {new_devices.DATA_ID: None,
                                   new_devices.SET_ID: None,
                                   new_devices.CLEAR_ID: None,
                                   new_devices.CLK_ID: None}

    assert nand_device.outputs == {None: new_devices.LOW}

    # Clock could be anywhere in its cycle
    assert clock_device.outputs in [{None: new_devices.LOW},
                                    {None: new_devices.HIGH}]

    assert dtype_device.outputs == {new_devices.Q_ID: new_devices.LOW,
                                    new_devices.QBAR_ID: new_devices.LOW}

    assert clock_device.clock_half_period == 5
    # Clock counter and D-type memory are initially at random states
    assert clock_device.clock_counter in range(5)
    assert dtype_device.dtype_memory in [new_devices.LOW, new_devices.HIGH]


@pytest.mark.parametrize("function_args, error", [
    ("(AND1_ID, new_devices.AND, 17)", "new_devices.INVALID_QUALIFIER"),
    ("(SW1_ID, new_devices.SWITCH, None)", "new_devices.NO_QUALIFIER"),
    ("(X1_ID, new_devices.XOR, 2)", "new_devices.QUALIFIER_PRESENT"),
    ("(D_ID, D_ID, None)", "new_devices.BAD_DEVICE"),
    ("(CL_ID, new_devices.CLOCK, 0)", "new_devices.INVALID_QUALIFIER"),
    ("(CL_ID, new_devices.CLOCK, 10)", "new_devices.NO_ERROR"),

    # Note: XOR device X2_ID will have been made earlier in the function
    ("(X2_ID, new_devices.XOR)", "new_devices.DEVICE_PRESENT"),
])
def test_make_device_gives_errors(new_devices, function_args, error):
    """Test if make_device returns the appropriate errors."""
    names = new_devices.names
    [AND1_ID, SW1_ID, CL_ID, D_ID, X1_ID,
     X2_ID] = names.lookup(["And1", "Sw1", "Clock1", "D1", "Xor1", "Xor2"])

    # Add a XOR device: X2_ID
    new_devices.make_device(X2_ID, new_devices.XOR)

    # left_expression is of the form: new_devices.make_device(...)
    left_expression = eval("".join(["new_devices.make_device", function_args]))
    right_expression = eval(error)
    assert left_expression == right_expression


def test_get_signal_name(devices_with_items):
    """Test if get_signal_name returns the correct signal name."""
    devices = devices_with_items
    names = devices.names
    [AND1, I1] = names.lookup(["And1", "I1"])

    assert devices.get_signal_name(AND1, I1) == "And1.I1"
    assert devices.get_signal_name(AND1, None) == "And1"


def test_get_signal_ids(devices_with_items):
    """Test if get_signal_ids returns the correct signal IDs."""
    devices = devices_with_items
    names = devices.names
    [AND1, I1] = names.lookup(["And1", "I1"])

    assert devices.get_signal_ids("And1.I1") == [AND1, I1]
    assert devices.get_signal_ids("And1") == [AND1, None]


def test_set_switch(new_devices):
    """Test if set_switch changes the switch state correctly."""
    names = new_devices.names
    # Make a switch
    [SW1_ID] = names.lookup(["Sw1"])
    new_devices.make_device(SW1_ID, new_devices.SWITCH, 1)
    switch_object = new_devices.get_device(SW1_ID)

    assert switch_object.switch_state == new_devices.HIGH

    # Set switch Sw1 to LOW
    new_devices.set_switch(SW1_ID, new_devices.LOW)
    assert switch_object.switch_state == new_devices.LOW
