import sys
import os

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
