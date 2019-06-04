#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys

import wx

from main_project.names import Names
from main_project.devices import Devices
from main_project.network import Network
from main_project.monitors import Monitors
from main_project.scanner import Scanner
from main_project.parse import Parser
from main_project.userint import UserInterface
from gmain_project.gui import Gui


def main():

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    [s1, s2] = devices.names.lookup(["S1","S2"])

    devices.make_switch(s1, 0)
    devices.make_switch(s2, 0)
    devices.make_gate(1, devices.names.query("NAND"), 2)
    devices.make_gate(2, devices.names.query("NAND"), 2)

    network.make_connection(s1, None, 1, devices.names.query("I1"))
    network.make_connection(s2, None, 2, devices.names.query("I2"))
    network.make_connection(1, None, 2, devices.names.query("I1"))
    network.make_connection(2, None, 1, devices.names.query("I2"))
    print(network.check_network())

    print(monitors.make_monitor(1,None))
    monitors.display_signals()

    userint = UserInterface(names, devices, network, monitors)
    userint.command_interface()


if __name__ == "__main__":
    main()
