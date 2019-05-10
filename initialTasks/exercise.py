#!/usr/bin/env python3

"""Preliminary exercises for Part IIA Project GF2."""
import sys
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    return open(path, 'r')


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    char = input_file.read(1)
    if char == '':
        return None
    else:
        return char


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    while True:
        char = input_file.read(1)
        if char.isspace():
            continue
        elif char == '':
            return None
        else:
            return char


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    # find start of number
    while True:
        char = input_file.read(1)
        if char.isdigit():
            num = char
            break
        elif char == '':
            return None

    # find end of number
    while True:
        char = input_file.read(1)
        if char.isdigit():
            num = num+char
        else:
            return [num, char]


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    while True:
        char = input_file.read(1)
        if char.isalpha():
            name = char
            while True:
                char = input_file.read(1)
                if char.isalnum():
                    name = name+char
                else:
                    return [name, char]

        elif char == '':
            return None


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        inpfile = arguments[0]
        print("\nNow opening file..."+inpfile)
        # Print the path provided and try to open the file for reading
        f = open_file(inpfile)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        while True:
            char = get_next_character(f)
            if char is None:
                break
            print(char, end='')

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        f = open_file(inpfile)
        while True:
            char = get_next_non_whitespace_character(f)
            if char is None:
                break
            print(char, end='')

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        f = open_file(inpfile)
        while True:
            num = get_next_number(f)
            if num is None:
                break
            print(num)

        print("\nNow reading names...")
        # Print out all the names in the filethe
        f = open_file(inpfile)
        while True:
            name = get_next_name(f)
            if name is None:
                break
            print(name)

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        f = open_file(inpfile)
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]
        while True:
            n = get_next_name(f)
            if n is None:
                break
            out = name.lookup(n[0])
            if out not in bad_name_ids:
                print(name.get_string(out))


if __name__ == "__main__":
    main()
