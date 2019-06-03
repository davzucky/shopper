import pytest

from shared.os_helpers import get_env_variable, get_env_variable_or_default


def test_get_env_variable_raise_exception_when_env_not_found():
    with pytest.raises(ReferenceError):
        get_env_variable("should raise")


def test_get_env_variable_return_value_when_exist_in_env(monkeypatch):
    key = "USER"
    value = "TestingUser"
    monkeypatch.setenv(key, value)

    return_value = get_env_variable(key)
    assert return_value == value


def test_get_env_variable_or_default_return_expected_value(monkeypatch):
    key = "USER"
    value = "TestingUser"
    monkeypatch.setenv(key, value)

    return_value = get_env_variable_or_default(key)
    assert return_value == value


def test_get_env_variable_or_default_return_default_value():
    key = "SOME_PARAM"
    default_value = "unknow"

    return_value = get_env_variable_or_default(key, default_value)
    assert return_value == default_value