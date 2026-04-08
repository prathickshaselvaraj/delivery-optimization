from delivery_optimizer import sorting_deliveries

def test_sorting_basic():
    data = [
        {'location_id': 'A', 'distance_from_warehouse': 10, 'priority': 'low', 'priority_value': 3},
        {'location_id': 'B', 'distance_from_warehouse': 5, 'priority': 'high', 'priority_value': 1},
        {'location_id': 'C', 'distance_from_warehouse': 7, 'priority': 'medium', 'priority_value': 2},
    ]

    sorted_data = sorting_deliveries(data)

    # High priority should come first
    assert sorted_data[0]['location_id'] == 'B'
