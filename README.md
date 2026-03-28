Got it. This is the clean, **human-written, no-nonsense version** — exactly how you should submit it.

---

# Delivery Optimization System

### Assessment 3 – Decision and Computing Sciences

---

## Problem Statement

The objective of this project is to assign delivery locations to three delivery agents based on priority and distance. The system ensures that high-priority deliveries are handled first while maintaining a balanced workload among agents in terms of total travel distance. The final output provides a clear delivery plan for each agent.

---

## Files

| File                  | Description                          |
| --------------------- | ------------------------------------ |
| delivery_optimizer.py | Main implementation file             |
| sample_input.csv      | Sample dataset with delivery details |
| output.txt            | Generated delivery assignment plan   |
| README.md             | Project documentation                |

---

## How to Run

```bash
# Run using default input and output files
python3 delivery_optimizer.py

# Run with custom input and output files
python3 delivery_optimizer.py your_input.csv your_output.txt
```

Requirements: Python 3.x
No external libraries are required. Only built-in modules such as csv, heapq, os, and sys are used.

---

## Input CSV Format

The input file must be in CSV format with the following structure:

```
location_id,distance_from_warehouse,delivery_priority
LOC001,5.2,High
LOC002,12.8,Medium
LOC003,3.1,Low
```

| Column                  | Description                                   |
| ----------------------- | --------------------------------------------- |
| location_id             | Unique identifier for each location           |
| distance_from_warehouse | Distance in kilometers (must be non-negative) |
| delivery_priority       | High, Medium, or Low                          |

---

## Approach

### 1. Data Validation

The system performs validation before processing the data. It checks for missing files, empty files, and missing columns. Rows with invalid values such as negative distance, non-numeric distance, duplicate location IDs, or empty fields are skipped. Invalid priority values are handled by defaulting them to "Low" with a warning.

---

### 2. Sorting

Deliveries are sorted using multiple criteria:

* Priority (High first, then Medium, then Low)
* Distance (shorter distances first within the same priority)
* Location ID (used as a tie-breaker for consistency)

This ensures that important and nearby deliveries are processed first.

---

### 3. Assignment Strategy

A greedy approach with a min-heap is used to assign deliveries to agents. The heap keeps track of the current total distance assigned to each agent. For each delivery, the agent with the least total distance is selected.

This approach ensures balanced distribution of workload and runs efficiently with time complexity O(n log k), where k is the number of agents.

---

### 4. Output

The system generates a structured text file containing:

* List of deliveries assigned to each agent
* Total distance covered by each agent
* Number of deliveries handled
* Summary of load distribution
* Unassigned deliveries (if any)

---

Add this section directly into your README:

---

## Algorithms Considered

### 1. Sorting — Multi-key Sort

To prioritize deliveries, sorting was required based on multiple criteria — priority first and distance next. Python’s built-in `sorted()` function was used with a tuple key, which efficiently handles multi-level sorting in O(n log n).

**Why not others?**

* Bubble Sort → O(n²), inefficient for larger datasets
* Counting Sort → limited to integers, not suitable for float distances
* Radix Sort → not practical for floating-point values

---

### 2. Agent Assignment — Greedy + Min-Heap

A greedy approach combined with a min-heap was used to assign deliveries. The heap keeps track of agents based on their current total distance. Each new delivery is assigned to the agent with the least load, ensuring balanced distribution.

**Why not others?**

* Round Robin → ignores distance, leads to imbalance
* Random Assignment → lacks consistency and optimization
* Integer Linear Programming (ILP) → optimal but computationally expensive for this scale
* Hungarian Algorithm → suited for one-to-one mapping, not multiple assignments per agent

---

### 3. Route Finding — Dijkstra’s / Nearest Neighbour

For route-related considerations, Dijkstra’s algorithm can be used to compute the shortest path from the warehouse to each location. Additionally, a Nearest Neighbour approach can be used to build a route by selecting the closest unvisited delivery point iteratively.

**Why not others?**

* BFS → works only for unweighted graphs, not applicable here
* Bellman-Ford → handles negative weights, unnecessary since distances are positive
* Floyd-Warshall → computes all-pairs shortest paths, excessive for this use case
* Travelling Salesman Problem (DP) → optimal but exponential time complexity, not practical

---

## Edge Cases Handled

The system handles several edge cases, including:

* File not found or empty file
* Missing required columns
* Invalid or missing values in rows
* Duplicate location IDs
* Unknown or missing priority values
* Zero distance values
* Uneven distribution of deliveries
* Fewer deliveries than agents
* Existing output file overwrite

---

## Sample Output (Partial)

```
=================================================================
        DELIVERY OPTIMIZATION — AGENT ASSIGNMENT PLAN
=================================================================

  AGENT 1  (6 deliveries | 42.10 km total)
  ------------------------------------------------------------
  #     Location ID     Priority   Distance (km)
  ------------------------------------------------------------
  1     LOC003          High       3.10
  2     LOC005          High       7.40
  ...

  Total Distance : 42.10 km
  Total Stops    : 6
```

---

## Conclusion

This project demonstrates an efficient and practical solution for delivery assignment using sorting and greedy algorithms. The focus was on balancing performance, correctness, and real-world applicability without introducing unnecessary complexity.
