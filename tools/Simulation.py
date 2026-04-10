from typing import Dict, List, Tuple, Set
from tools.Connection import Connection


class Simulation():
    '''The conductor of the system.
    Responsibility:
    Manage the "Turn" loop.
    It asks every Drone what it wants to do,
    asks every Zone/Connection if that action is allowed,
    updates the state, and prints the output.'''

    @classmethod
    def find_all_paths(
        cls,
        graph: Dict[str, list[Tuple[str, Connection]]],
        start: str,
        end: str
    ) -> List[List[str]]:
        all_paths: List[List[str]] = []
        # Stack stores tuples: (current_node, path_so_far, visited_nodes)
        stack: List[Tuple[str, List[str], Set[str]]] = [
            (start, [start], {start})]
        current: str
        path: List[str]
        visited: Set[str]

        while stack:
            current, path, visited = stack.pop()

            if current == end:
                # remove the start zone as all drones have that pos by default
                path.pop(0)
                all_paths.append(path)
                continue

            for neighbor, _ in graph[current]:
                # Assume graph[zone] returns list of connected zones
                # Check if neighbor is blocked or already visited in this path
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_visited = visited | {neighbor}
                    stack.append((neighbor, new_path, new_visited))

        return all_paths

    @staticmethod
    def _extract_path(
            parent: Dict[str, str],
            start_zone: str,
            end_zone: str
    ) -> List[str]:
        # maybe convert the string path to a list of points
        # - cu = end
        curent_location: str = end_zone
        result: List[str] = []
        # - while cu != start:
        while curent_location != start_zone:
            # - result.append(cu)
            result.append(curent_location)
            # cu = parent[cu]
            curent_location = parent[curent_location]
            # - reverse result and return it
        return result[::-1]
