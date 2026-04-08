"""
Test suite for the broken_app.py
These tests will be used by the verify_health tool.
"""
import pytest
from broken_app import calculate_average, get_user_data


def test_calculate_average_with_valid_data():
    """Test that calculate_average works with valid input."""
    result = calculate_average([10, 20, 30])
    assert result == 20.0


def test_calculate_average_with_empty_list():
    """Test that calculate_average handles empty list."""
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


def test_get_user_data_valid_id():
    """Test that get_user_data returns correct user."""
    user = get_user_data(1)
    assert user["name"] == "Alice"
    assert user["age"] == 30


def test_get_user_data_invalid_id():
    """Test that get_user_data handles invalid user ID."""
    with pytest.raises(KeyError):
        get_user_data(999)


def test_calculate_average_single_value():
    """Test calculate_average with single value."""
    result = calculate_average([42])
    assert result == 42.0


def test_get_user_data_second_user():
    """Test fetching second user."""
    user = get_user_data(2)
    assert user["name"] == "Bob"
    assert user["age"] == 25

# Made with Bob
