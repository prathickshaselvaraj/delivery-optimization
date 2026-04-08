import sys
import os
import pytest

# Fix import path for Jenkins
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from delivery_optimizer import sorting_deliveries


def test_sorting_basic():
    data = [
        {"location_id": "A", "distance_from_warehouse": 10, "priority_value": 2},
        {"location_id": "B", "distance_from_warehouse": 5, "priority_value": 1},
    ]

    result = sorting_deliveries(data)

    assert result[0]["location_id"] == "B"
    assert result[1]["location_id"] == "A"


def test_empty_list():
    result = sorting_deliveries([])
    assert result == []


def test_single_element():
    data = [{"location_id": "A", "distance_from_warehouse": 10, "priority_value": 2}]
    result = sorting_deliveries(data)

    assert result == data


def test_same_priority_sort_by_distance():
    data = [
        {"location_id": "A", "distance_from_warehouse": 20, "priority_value": 1},
        {"location_id": "B", "distance_from_warehouse": 5, "priority_value": 1},
    ]

    result = sorting_deliveries(data)

    assert result[0]["location_id"] == "B"


def test_already_sorted():
    data = [
        {"location_id": "B", "distance_from_warehouse": 5, "priority_value": 1},
        {"location_id": "A", "distance_from_warehouse": 10, "priority_value": 2},
    ]

    result = sorting_deliveries(data)

    assert result == data


def test_reverse_sorted():
    data = [
        {"location_id": "A", "distance_from_warehouse": 50, "priority_value": 3},
        {"location_id": "B", "distance_from_warehouse": 20, "priority_value": 2},
        {"location_id": "C", "distance_from_warehouse": 5, "priority_value": 1},
    ]

    result = sorting_deliveries(data)

    assert result[0]["location_id"] == "C"


def test_large_dataset():
    data = [
        {"location_id": str(i), "distance_from_warehouse": i, "priority_value": i % 5}
        for i in range(100)
    ]

    result = sorting_deliveries(data)

    assert len(result) == 100


def test_missing_keys():
    data = [{"location_id": "A"}]

    with pytest.raises(Exception):
        sorting_deliveries(data)


def test_invalid_input_type():
    with pytest.raises(Exception):
        sorting_deliveries("invalid")
