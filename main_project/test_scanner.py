import pytest
from names import Names
from scanner import Scanner, Symbol

'''Test the scanner module'

list of functions to test:
get_symbol
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


def test_get_name_and_num(new_scanner, new_names):
    """check that the get_name function gives out a valid name and the next character,
    check that the name is an alphanumerical string"""
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


@pytest.mark.parametrize("data, expected_output_type, expected_output_id", [("  gates", None, None), ("DEVICES",
0,"ignore"),("NAND",3, "ignore"),("device", 1, "ignore"),
("A12J", 3, "ignore"), (";", 8,"ignore"),("12", 2, "ignore")])
def test_get_symbol(new_names, data, expected_output_type, expected_output_id):
    print(data)
    test_scan = Scanner(data, new_names, True)
    val = test_scan.get_symbol()
    print(v
    if test_scan in test_scan.ignore:
        assert val == expected_output_type
    else:
        assert 0
        #assert val.type == expected_output_type

#check add_name detects names only
    #ignore
    #heading
    #keyword
    #device
    #names
#check punctuation
    #one type
    #nonvalid
#check word number is increasing
#arrow
#digit
#eof



#check add_number
#check list_of_ignores
#

# TODO: def test_get_symbol()


# TODO: def test_error()

