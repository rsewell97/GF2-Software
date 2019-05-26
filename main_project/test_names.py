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
        my_name.lookup([name])
    return my_name


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("tag, id", [("Lea",0), ("Robbie",1), ("Dan", 2)])
def test_get_name(new_names, name_string_list, used_names, tag, id):
    assert used_names.get_name_string(id) == tag
    assert new_names.get_name_string(id) is None


@pytest.mark.parametrize("tag, id", [("Lea",0), ("Robbie",1), ("Dan", 2)])
def test_query(new_names, name_string_list, used_names, tag, id):
    assert used_names.query(tag) == id
    assert new_names.query(tag) is None


def test_lookup_append(used_names):
    """Checks that lookup appends a name if it is not already in the class"""
    before = len(used_names.names)
    used_names.lookup(["Andrew"])
    after = len(used_names.names)
    assert before + 1 == after


def test_lookup_unique_id(used_names,name_string_list):
    """Test to check that all the of the name ids are unique"""
    for i in range(0,2):
        for j in range(0,2):
            if i != j:
                assert not used_names.query(name_string_list[i]) == used_names.query(name_string_list[j])
            elif i == j:
                assert used_names.query(name_string_list[i]) == used_names.query(name_string_list[j])
            else:
                break



def test_lookup_raises_exceptions(used_names):
    """ Test if lookup raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.lookup(12)
    # with pytest.raises(TypeError):
    #     used_names.lookup("string")
    # TODO: ROBBIE IS GOING TO WRITE AN ERROR IF IT ISN'T A 1 VALUED LIST RATHER THAN A SINGLE STRING


def test_combination_funcs(name_string_list,used_names):
    """Check that the query function on a single string works the same as the lookup function on an index list"""
    i = 0
    for name in name_string_list:
        print (used_names.lookup(name)[i])
        print(used_names.get_name_string(used_names.lookup(name_string_list)[i]))
        assert used_names.lookup(name)[i] == used_names.query(name[i])
        assert name_string_list[i] == used_names.get_name_string(used_names.lookup(name_string_list)[i])
        i +=1


def test_types(used_names,name_string_list):
    """Makes sure that the expected type of value is coming out of the three main functions"""
    i = 0
    while i <= 2:
        assert (type(used_names.get_name_string(used_names.lookup(name_string_list)[i]))) is str
        assert (type(used_names.lookup(name_string_list)[i])) is int
        assert (type(used_names.query(name_string_list[i]))) is int
        i += 1


def test_error_code(new_names):
    assert len(new_names.unique_error_codes(5)) == 5