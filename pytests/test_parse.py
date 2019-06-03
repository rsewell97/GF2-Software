"""Test the parse module

Writen by Lea """
import pytest

from main_project.names import Names
from main_project.scanner import Scanner
from main_project.network import Network
from main_project.devices import Devices
from main_project.parse import Parser
from main_project.monitors import Monitors
from main_project.error import SyntaxError, SemanticError, ValueError, UnclassedError

# #@pytest.fixture()
# def trying_something():
#     print(__name__)
#     return True


def raise_errors(error):
    if error == SemanticError:
        raise SemanticError
    elif error == SyntaxError:
        raise SyntaxError
    elif error == ValueError:
        raise ValueError
    else:
        raise UnclassedError

# def test_error_fun():
#     with pytest.raises(SemanticError):
#         raise_errors(SemanticError)
#     with pytest.raises(SyntaxError):
#

def startup_parser(data):
    new_names = Names()
    new_scan = Scanner(data, new_names, True)
    new_devices = Devices(new_names)
    new_network= Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    parse = Parser(new_names, new_devices, new_network, new_monitors, new_scan)
    return parse


@pytest.mark.parametrize("input, expected_outputs",
                         [("devices{} connections{}", True),
                          ("devices{} monitor{} connections{}", True),
                          ("devices{} connections{} monitor{}", True),
                          ])
def test_heading_recognition(input, expected_outputs):
    #trying_something()
    new_parser = startup_parser(input)
    new_parser.parse_network()
    bool = new_parser.found_devices and new_parser.found_connections or new_parser.found_monitor
    assert bool == expected_outputs


@pytest.mark.parametrize("input", ["devices{}", "connections{} devices{}"])
def test_heading_ordering(input):
    new_parser = startup_parser(input)
    with pytest.raises(SyntaxError):
        new_parser.parse_network()


@pytest.mark.parametrize("inputs, id", [("{ A is NAND gate; B is a DTYPE; A has 2 inputs;}",0 ),  # works
                                            ("A is a NAND gate; B is a DTYPE; A has 2 inputs;", 1),  # need curlies - syntax
                                            ("{A is a NAND gate; B is a DTYPE;}", 2)])  # NAND gates need num of inputs defined - semantic
def test_devices_section(inputs, id):
    new_parser = startup_parser(inputs)
    if id == 0:
        new_parser.parse_section('devices')
        assert new_parser.parse_error_count == 0
    elif id == 1:
        with pytest.raises(SyntaxError):
            new_parser.parse_section('devices')
    elif id == 2:
        with pytest.raises(SemanticError):
            new_parser.parse_section('devices')


@pytest.mark.parametrize("string, id",
                         [("{device A {S1 to A.I1; S1 to A.I2;}}",0),  # works
                            ("{device A {S1 to A.I1;}}",1),  # not all inputs are connected - semantic
                            ("{device A {S1 to A.I1; S1 to A.I2}}",2),  # missing semi colon - syntax
                            ("{device B {S1 to A.I1; S1 to A.I2;}}",3)]  # device not defined - semantic
                          )
def test_connections_section(string,id):
    device_init = "devices{A is a NAND gate; S1 is SWITCH; A has 2 inputs;} connections"
    input = device_init + string
    print (input)
    new_parser = startup_parser(input)
    if id == 0:
        new_parser.parse_network()
        assert new_parser.parse_error_count == 0
    elif id == (1 or 3):
        with pytest.raises(SemanticError):
            new_parser.parse_network()
    elif id == 2:
        with pytest.raises(SyntaxError):
            new_parser.parse_network()
    else:
        assert 1



@pytest.mark.parametrize("inputs, id", [
        ("{A;}", 0),
        ("{A,B;}", 1),  # undefined name - semantic
        ("{A,A;}", 2),  # double defined - semantic
        ("{12;}", 3)])  # not a valid name - syntax
def test_parse_monitor(inputs, id):
    device_init = "devices{A is a NAND gate; S1 is SWITCH; A has 2 inputs;} " \
                  "connections{device A{S1 to A.I1; S1 to A.I2;}} monitor"
    input = device_init + inputs
    print(input)
    new_parser = startup_parser(input)
    if id == 0:
        new_parser.parse_network()
        assert new_parser.parse_error_count == 0
    elif id == (1 or 2):
        with pytest.raises(SemanticError):
            new_parser.parse_network()
    elif id == 3:
        with pytest.raises(SyntaxError):
            new_parser.parse_network()

    else:
        assert 1



