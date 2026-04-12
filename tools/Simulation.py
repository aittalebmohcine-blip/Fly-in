"""Simulation orchestration module for Fly_in.

Defines helper routines to compute routes, remove the start node from solutions,
and support the simulation turn loop.
"""
from typing import Dict, List, Tuple, Set
from tools.Connection import Connection


class Simulation:
    '''The conductor of the system.
    Manages the turn loop and path discovery operations.'''

    @staticmethod
    def remove_start_from_solutions(
        solutions: List[List[str]]
    ) -> None:
        """Remove the initial start node from each valid path."""
        for solution in solutions:
            solution.pop(0)

    @classmethod
    def find_all_paths(
        cls,
        graph: Dict[str, List[Tuple[str, Connection]]],
        start: str,
        end: str
    ) -> List[List[str]]:
        """Breadth-first search to discover all simple paths between nodes."""
        all_paths: List[List[str]] = []
        # Use a DFS stack to explore all possible simple paths.
        stack: List[Tuple[str, List[str], Set[str]]] = [
            (start, [start], {start})]

        while stack:
            current, path, visited = stack.pop()
            if current == end:
                all_paths.append(path)
                continue

            for neighbor, _ in graph[current]:
                if neighbor not in visited:
                    new_path: List[str] = path + [neighbor]
                    new_visited: Set[str] = visited | {neighbor}
                    stack.append((neighbor, new_path, new_visited))

        return all_paths

    @staticmethod
    def _extract_path(
            parent: Dict[str, str],
            start_zone: str,
            end_zone: str
    ) -> List[str]:
        """Reconstruct a path from parent pointers."""
        current_location: str = end_zone
        result: List[str] = []
        while current_location != start_zone:
            result.append(current_location)
            current_location = parent[current_location]
        return result[::-1]
