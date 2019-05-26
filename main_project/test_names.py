"""Test the names module."""
import pytest
from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Lea", "Robbie", "Dan"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    for name in name_string_list:
        my_name.lookup(name)
    return my_name


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("tag, id", [("Lea",7), ("Robbie",2), ("Dan", 8)])
def test_expected_outputs(new_names, used_names, tag, id):
    print(used_names(tag))
    #print(new_names.get_name_string(id))
    #print(used_names.get_name_string(id))
    assert 0

# def test_lookup_raises_exceptions(name_string_list):
#     """ Test if lookup raises expected exceptions."""
#     with pytest.raises(TypeError):
#         name_string_list.lookup(12)
#     with pytest.raises(TypeError):
#         name


def test_combination_funcs(name_string_list,used_names):
    '''Check that the query function on a single string works the same as the lookup function on an index list'''
    i = 0
    for name in name_string_list:
        assert used_names.lookup(name)[i] == used_names.query(name[i])
        assert name_string_list[i] == used_names.get_name_string(used_names.lookup(name_string_list)[i])
        i +=1


def test_types(used_names,name_string_list):
    i = 0
    while i <= 2:
        assert (type(used_names.get_name_string(used_names.lookup(name_string_list)[i]))) is str
        assert (type(used_names.lookup(name_string_list)[i])) is int
        assert (type(used_names.query(name_string_list[i]))) is int
        i += 1

# def test_query(used_names, name_string_list):
#     #used_names.lookup(name_string_list)
#     (used_names.query("Lea"))
#     print(used_names.query("Robbie"))
#     print(used_names.query("Dan"))
#     assert 0