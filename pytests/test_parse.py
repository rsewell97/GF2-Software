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


def startup_parser(data):
    new_names = Names()
    new_scan = Scanner(data, new_names, True)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    parse = Parser(new_names, new_devices, new_network, new_monitors, new_scan)
    return parse


@pytest.mark.parametrize("input, expected_outputs",
                         [("devices{} connections{}", True),
                          ("devices{} monitor{} connections{}", True),
                          ("devices{} connections{} monitor{}", True),
                          ])
def test_heading_recognition(input, expected_outputs):
    # trying_something()
    new_parser = startup_parser(input)
    new_parser.parse_network()
    bool = new_parser.found_devices and new_parser.found_connections or new_parser.found_monitor
    assert bool == expected_outputs


@pytest.mark.parametrize("input", ["devices{}", "connections{} devices{}", "devices{device A{}}"])
def test_heading_ordering(input):
    new_parser = startup_parser(input)
    with pytest.raises(SyntaxError):
        new_parser.parse_network()


@pytest.mark.parametrize("inputs, id", [("{ A is NAND gate; B is a DTYPE; A has 2 inputs;}", 0),  # works
                                        # need curlies - syntax
                                        ("A is a NAND gate; B is a DTYPE; A has 2 inputs;", 1),
                                        ("{A is a NAND gate; B is a DTYPE;}", 2), # NAND gates need num of inputs defined - semantic
                                        ("{A is a NAND gate; B is a DTYPE; A has 18 inputs}", 2), # max ins is 16
                                        ("{A is a SIGGEN; A has trace 10001;}",0)])  # works
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
                         [("{device A {S1 to A.I1; S1 to A.I2;}}", 0),  # works
                          # not all inputs are connected - semantic
                          ("{device A {S1 to A.I1;}}", 1),
                          # missing semi colon - syntax
                          ("{device A {S1 to A.I1; S1 to A.I2}}", 2),
                            # missing dot - syntax
                          ("{device A {S1 to AI1; S1 to A.I2;}}", 3),
                          ("{device B {S1 to A.I1; S1 to A.I2;}}", 3)]  # device not defined - semantic
                         )
def test_connections_section(string, id):
    device_init = "devices{A is a NAND gate; S1 is SWITCH; A has 2 inputs;} connections"
    input = device_init + string
    print(input)
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


@pytest.mark.parametrize("string, id",
                         [("{A1=>A4 are NAND gates;A1=>A4 have 2 inputs;}", 0),  # works
                          # name base inconsistent - syntax
                          ("{A1=>B4 are NAND gates;A1=>A4 have 2 inputs;}", 1),
                          # named more than two devices to delimit range - syntax
                          ("{A1=>A3 A5 are NAND gates;A1=>A4 have 2 inputs;}", 1),
                          ("{A6=>A1 are NAND gates;A1=>A4 have 2 inputs;}", 2)])
def test_range_notation(string, id):
    new_parser = startup_parser(string)
    if id == 0:
        new_parser.parse_section('devices')
        assert new_parser.parse_error_count == 0
    elif id == 1:
        with pytest.raises(SyntaxError):
           new_parser.parse_section('devices')
    elif id == 2:
        with pytest.raises(ValueError):
            new_parser.parse_section('devices')


@pytest.fixture
def big_test_file():
    string = """DEVICES {
   A is XOR;
   B is AND;
   C is NAND;
   D is OR;
   E is NOR;
   F is DTYPE;
   G is NAND;
   H is OR;
   A,B,C,D,G,H have 2 inputs;
   E has 3 inputs;
   S1 => S3 are SWITCH;
   S2 set 1;
   CKL1 is CLOCK;
   CKL1 has cycle 5;
}

CONNECTIONS {
   device A {
       S1 to A.I1;
       S2 to A.I2;
   }
   device B {
       S1 to B.I1;
       S3 to B.I2;
   }
   device C {
       S2 to C.I1;
       B to C.I2;
   }
   device D {
       A to D.I1;
       B to D.I2;
   }
   device E {
       D to E.I1;
       S2 to E.I2;
       C to E.I3;
   }
   device F {
        CKL1 to F.CLK;
        D to F.SET;
        C to F.CLEAR;
        S2 to F.DATA;
   }
   device G {
       E to G.I1;
       F.Q to G.I2;
   }
   device H {
       C to H.I1;
       F.QBAR to H.I2;
   }
}

MONITOR {
   B, F.Q, CKL1;
}"""

    return string


def test_d_type(big_test_file):
    new_parser = startup_parser(big_test_file)
    assert new_parser.parse_network() is True
