"""
Greedy Best-First Search implementation for TSP (clean, self-contained).

This module contains a single class `GreedyBestFirstSearchTSP` which is
the refactored version of the original solver. The implementation focuses
on clarity: the heuristic used, the main loop, and the step callback are
kept explicit and well-documented.
"""
import time


class GreedyBestFirstSearchTSP:
    """Greedy Best-First Search for TSP.

    Behaviour:
    - Heuristic h(n) = distance from candidate city to the goal (start city).
    - At each step choose the unvisited city with smallest h(n).
    - This is intentionally simple (greedy) and is the algorithm showcased
      by the application.
    """

    def __init__(self, distance_matrix, city_names, coordinates):
        self.distance_matrix = distance_matrix
        self.city_names = city_names
        self.coordinates = coordinates
        self.n_cities = len(city_names)
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0  # Đếm số phép tính/so sánh

    def heuristic(self, city, goal_city):
        """Return heuristic h(n): straight from distance matrix."""
        return self.distance_matrix[city][goal_city]

    def solve(self, start_city=0, step_callback=None):
        """Solve TSP using Greedy Best-First Search.

        Args:
            start_city: index of starting city
            step_callback: optional callable called with step info dict

        Returns:
            (route, total_distance)
        """
        current_city = start_city
        goal_city = start_city
        visited = [False] * self.n_cities
        visited[current_city] = True
        route = [current_city]
        total_distance = 0

        # initial step record
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0
        self.steps.append({
            'step': 0,
            'current': self.city_names[current_city],
            'current_idx': current_city,
            'next': None,
            'next_idx': None,
            'distance': 0,
            'total_distance': 0,
            'visited': route.copy(),
            'candidates': []
        })

        if step_callback:
            step_callback(self.steps[-1])

        # main greedy loop
        for step in range(self.n_cities - 1):
            best_heuristic = float('inf')
            next_city = None
            candidates = []

            for city in range(self.n_cities):
                if not visited[city]:
                    self.nodes_explored += 1
                    self.operations += 2  # 2 lookups trong distance_matrix
                    g_cost = self.distance_matrix[current_city][city]
                    h_cost = self.heuristic(city, goal_city)

                    candidates.append({
                        'city': self.city_names[city],
                        'city_idx': city,
                        'distance': g_cost,
                        'heuristic': h_cost
                    })

                    self.operations += 1  # 1 comparison
                    if h_cost < best_heuristic:
                        best_heuristic = h_cost
                        next_city = city

            if next_city is None:
                break

            actual_distance = self.distance_matrix[current_city][next_city]
            visited[next_city] = True
            route.append(next_city)
            total_distance += actual_distance

            step_info = {
                'step': step + 1,
                'current': self.city_names[current_city],
                'current_idx': current_city,
                'next': self.city_names[next_city],
                'next_idx': next_city,
                'distance': actual_distance,
                'heuristic': best_heuristic,
                'total_distance': total_distance,
                'visited': route.copy(),
                'candidates': candidates
            }
            self.steps.append(step_info)

            if step_callback:
                step_callback(step_info)
                time.sleep(0.5)

            current_city = next_city

        # return to start
        return_distance = self.distance_matrix[current_city][start_city]
        route.append(start_city)
        total_distance += return_distance

        self.steps.append({
            'step': len(route) - 1,
            'current': self.city_names[current_city],
            'current_idx': current_city,
            'next': self.city_names[start_city],
            'next_idx': start_city,
            'distance': return_distance,
            'total_distance': total_distance,
            'visited': route.copy(),
            'candidates': []
        })

        if step_callback:
            step_callback(self.steps[-1])

        return route, total_distance
