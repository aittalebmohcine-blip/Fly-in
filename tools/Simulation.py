from typing import Dict, Tuple, List, Set
from tools.Connection import Connection


class Simulation():
    '''The conductor of the system.
    Responsibility:
    Manage the "Turn" loop.
    It asks every Drone what it wants to do,
    asks every Zone/Connection if that action is allowed,
    updates the state, and prints the output.'''

    @classmethod
    def find_the_shortest_path(
        cls,
        graph: Dict[str, list[Tuple[str, Connection]]],
        start_zone: str,
        end_zone: str
    ) -> list[str]:
        '''Find the shortest path from start_zone to
        end_zone using BFS's algorithm.'''
        # - initialize the queue, visited set, parent dictionary
        # and current location
        queue: List[str] = [start_zone]
        visited: Set[str] = {start_zone}
        parent: Dict[str, str] = {start_zone: start_zone}
        current_location: str
        paths: List[List[str]] = []

        # - loop until the queue is empty:
        while queue:
            # - current_zone is always the first element that gets in the queue
            current_location = queue.pop(0)
            visited.add(current_location)
            # - for each unvisited neighbor of current_zone:
            for neighbour, _ in graph[current_location]:
                if neighbour not in visited:
                    # - curent_location is the prarent of its neighbors
                    parent[neighbour] = current_location
                    # - if we reached the end_zone, we can stop searching
                    if neighbour == end_zone:
                        # - extract path from parent dictionary and return it
                        paths.append(cls._extract_path(
                            parent, start_zone, end_zone))
                    # mark neighbor as visited
                    # visited.add(neighbour)
                    # - add it to the queue
                    queue.append(neighbour)
        print(paths)
        exit(0)
        return []

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
