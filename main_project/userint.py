"""Implement the interactive command line user interface.

Used in the Logic Simulator project to enable the user to enter commands
to run the simulation or adjust the network properties.

Classes:
--------
UserInterface - reads and parses user commands.
"""


class UserInterface:

    """Read and parse user commands.

    This class allows the user to enter certain commands.
    These commands enable the user to run or continue the simulation for a
    number of cycles, set switches, add or zap monitors, show help, or quit
    the program.

    Parameters
    -----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods:
    ---------------
    command_interface(self): Reads in the commands and calls the corresponding
                             functions.

    get_line(self): Prints a prompt for the user and updates the user entry.

    read_command(self): Returns the first non-whitespace character.

    get_character(self): Moves the cursor forward by one character in the user
                         entry.

    skip_spaces(self): Skips whitespace characters until a non-whitespace
                       character is reached.

    read_string(self): Returns the next alphanumeric string.

    read_name(self): Returns the name ID of the current string.

    read_signal_name(self): Returns the device and port IDs of the current
                            signal name.

    read_number(self, lower_bound, upper_bound): Returns the current number.

    help_command(self): Prints a list of valid commands.

    switch_command(self): Sets the specified switch to the specified signal
                          level.

    monitor_command(self): Sets the specified monitor.

    zap_command(self): Removes the specified monitor.

    run_network(self, cycles): Runs the network for the specified number of
                               simulation cycles.

    run_command(self): Runs the simulation from scratch.

    continue_command(self): Continues a previously run simulation.
    """

    def __init__(self, names, devices, network, monitors):
        """Initialise variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

    def command_interface(self):
        """Read the command entered and call the corresponding function."""
        print("Logic Simulator: interactive command line user interface.\n"
              "Enter 'h' for help.")
        self.get_line()  # get the user entry
        command = self.read_command()  # read the first character
        while command != "q":
            if command == "h":
                self.help_command()
            elif command == "s":
                self.switch_command()
            elif command == "m":
                self.monitor_command()
            elif command == "z":
                self.zap_command()
            elif command == "r":
                self.run_command()
            elif command == "c":
                self.continue_command()
            else:
                print("Invalid command. Enter 'h' for help.")
            self.get_line()  # get the user entry
            command = self.read_command()  # read the first character

    def get_line(self):
        """Print prompt for the user and update the user entry."""
        self.cursor = 0
        self.line = input("#: ")
        while self.line == "":  # if the user enters a blank line
            self.line = input("#: ")

    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print("Error! Expected a name.")
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print("Error! Expected a number.")
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print("Number out of range.")
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print("Number out of range.")
                return None

        return number

    def help_command(self):
        """Print a list of valid commands."""
        print("User commands:")
        print("r N       - run the simulation for N cycles")
        print("c N       - continue the simulation for N cycles")
        print("s X N     - set switch X to N (0 or 1)")
        print("m X       - set a monitor on signal X")
        print("z X       - zap the monitor on signal X")
        print("h         - help (this command)")
        print("q         - quit the program")

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name()
        if switch_id is not None:
            switch_state = self.read_number(0, 1)
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    print("Successfully set switch.")
                else:
                    print("Error! Invalid switch.")

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
