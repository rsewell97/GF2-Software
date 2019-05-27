import pytest
from names import Names
from scanner import Scanner, Symbol

'''Test the scanner module'

list of functions to test:
get_symbol
get_name
get_number
skip_spaces
advance
error
'''


@pytest.fixture
def new_scanner():
    data = ("   device, 12 has ")
    names = Names()
    symbol = Symbol()
    scan = Scanner(data, names, True)
    return scan


@pytest.fixture
def no_spaces():
    return ["d" , "e" , "v" , "i" , "c" , "e" , "," , "1", "2" , "h" , "a" , "s" ]


def test_skip_spaces(new_scanner, expected_out = "d"):
    new_scanner.skip_spaces()
    assert new_scanner.current_character == expected_out


def test_advance(new_scanner, no_spaces):
    i=0
    print(no_spaces[i])
    while i <= len(no_spaces)-1:
        expected = no_spaces[i]
        print(no_spaces[i])
        new_scanner.skip_spaces()
        assert new_scanner.current_character == expected
        new_scanner.advance()
        i += 1


# TODO: def new_scanned_item()


# TODO: def test_get_symbol()


# TODO: def test_get_name()


# TODO: def test_get_number()


# TODO: def test_skip_spaces()


# TODO: def test_advance()


# TODO: def test_error()

