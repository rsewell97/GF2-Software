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
def new_names():
    names = Names()
    return names


@pytest.fixture
def new_symbol():
    symbol = Symbol()
    return symbol


@pytest.fixture
def new_scanner():
    data = ("   device7, 12 has ")
    other_names = Names()
    scan = Scanner(data, other_names, True)
    return scan


@pytest.fixture
def no_spaces():
    return ["d" , "e" , "v" , "i" , "c" , "e" , "7" , "," , "1", "2" , "h" , "a" , "s" ]


def test_new_scanned_item_functionality(new_names):
    with pytest.raises(FileNotFoundError):
        Scanner("fakefile.txt", new_names, False)


def test_skip_spaces(new_scanner, new_names, expected_out = "d"):
    new_scanner.skip_spaces()
    assert new_scanner.current_character == expected_out


def test_advance(new_scanner, no_spaces):
    i=0
    while i <= len(no_spaces)-1:
        expected = no_spaces[i]
        new_scanner.skip_spaces()
        assert new_scanner.current_character == expected
        new_scanner.advance()
        i += 1


def test_get_name(new_scanner, new_names):
    """check that the get_name function gives out a valid name and the next character, check that the name is an alphanumerical string"""
    new_scanner.skip_spaces()
    name = new_scanner.get_name()
    assert name[0] == "device7"
    assert name [1] == ","
    assert name[0].isalnum()
    new_scanner.advance()
    new_scanner.advance()
    number = new_scanner.get_number()
    assert number[0] == "12"
    assert number[1] == " "






# TODO: def test_get_symbol()


# TODO: def test_get_name()


# TODO: def test_get_number()


# TODO: def test_error()

