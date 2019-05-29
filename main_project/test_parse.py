"""Test the parse module"""
import pytest

from names import Names
from scanner import Scanner
from network import Network
from devices import Devices
from parse import Parser
from monitors import Monitors
from error import SyntaxError , SemanticError , ValueError, UnclassedError


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
                          ("devices{}", False),
                          ("connections{} devices{}", False)])
def test_heading_ordering(input, expected_outputs):
    new_parser = startup_parser(input)
    
    new_parser.parse_network()
    print ("Has the parser found the heading devices?", new_parser.found_devices)
    print("Has the parser found the heading connection?", new_parser.found_connections)
    print("Has the parser found the heading monitors?", new_parser.found_monitor)
    bool = new_parser.found_devices and new_parser.found_connections or new_parser.found_monitor
    if not new_parser.found_devices:
        with pytest.raises(SyntaxError):
            new_parser.parse_network()
    else:
        pass
    assert bool == expected_outputs


# @pytest.mark.parametrize("input, expected outputs",
#                          [("{A is a NAND gate; B is a DTYPE;}", True),
#                             ("A is a NAND gate; B is a DTYPE;", False)])
# def test_finds_start_section(input, expected_outputs):
#     new_parser = startup_parser(input)
#     new_parser.parse_heading('devices')


def test_parse_devices_defined():

    assert 1


def test_parse_connections():
    assert 1


def test_parse_monitor():
    assert 1


#


# TODO:
# TODO: HEADINGS order of heading names, finding heading names robustly, how it handles not finding a heading name
# TODO: SECTIONS finds start and end of section
# TODO: DEVICES
# TODO: CONNECTIONS
# TODO: MONITOR

