from FuzzGenerator import process_config


def test_empty_config():
    assert process_config("") == {}


def test_single_boolean_config():
    assert process_config("--testopt") == {"testopt": "TRUE"}


def test_single_numeric_config():
    assert process_config("--testint 4") == {"testint": "4"}


def test_multiple_boolean_config():
    assert process_config("--a --b") == {"a": "TRUE", "b": "TRUE"}


def test_multiple_enum_config():
    assert process_config("--test1 A --test2 BB") == {"test1": "A", "test2": "BB"}


def test_multiple_mixed_config():
    assert process_config("--test1 1 --test2 --test3 ENUM --test4 --test5") == {"test1": "1",
                                                                                "test2": "TRUE",
                                                                                "test3": "ENUM",
                                                                                "test4": "TRUE",
                                                                                "test5": "TRUE"}
