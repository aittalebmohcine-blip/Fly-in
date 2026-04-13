"""Map model for Fly_in.

Holds zones, connections, and drones. Provides map validation,
route filtering, and turn advancement logic for the simulation.
"""
try:
    from termcolor import colored
except ImportError:
    print("Error: 'termcolor' is not installed."
          " Please install it using 'pip install termcolor pydantic'.")
    exit(1)
from pydantic import BaseModel

from typing import Dict, Tuple, List

from Drone import Drone
from Connection import Connection
from Zone import Zone
from Definitions import DroneStatus, ZoneType, EdgeType


class Map(BaseModel):
    '''Represents the fly-in map, including all zones,
    connections, and drones.'''
    nb_drones: int = 0
    zones: Dict[str, Zone] = {}
    connections: Dict[Tuple[str, str], Connection] = {}
    drones: Dict[str, Drone] = {}
    graph: Dict[str, list[Tuple[str, Connection]]] = {}

    def init_drones_at_start(self, start: str) -> None:
        """gives every drone the start name as the initial location"""
        for drone in self.drones.values():
            drone.loc = start

    def verify_start_goal_in_graph(self) -> None:
        """Confirm that both start and goal nodes exist in the graph."""
        start, goal = self.extract_start_goal_names()
        s_exist: bool = False
        g_exist: bool = False
        for node in self.graph.keys():
            if node == start:
                s_exist = True
            elif node == goal:
                g_exist = True
        if not all((s_exist, g_exist)):
            raise RuntimeError(
                "GRAPH ERROR: make sure there is a "
                "link between start and end hubs")

    def extract_start_goal_names(self) -> Tuple[str, str]:
        """Return the names of the start and end zones."""
        start: str = ""
        goal: str = ""
        for zone_name, zone in self.zones.items():
            if zone.edge == EdgeType.START:
                start = zone_name
            if zone.edge == EdgeType.END:
                goal = zone_name
        return start, goal

    @staticmethod
    def verify_solutions(
        solutions: List[List[str]],
        start: str,
        goal: str
    ) -> None:
        """Validate that at least one path connects the start and goal."""
        for solution in solutions:
            if solution[0] == start and solution[-1] == goal:
                return
        raise RuntimeError(
            "GRAPH ERROR: make sure there is a link between start and end hubs"
        )

    def build_graph(self) -> None:
        """Build the graph adjacency list from zone connections."""
        for connection in self.connections:
            zone1, zone2 = connection
            # Add both directions because connections are undirected.
            if self.graph.get(zone1) is not None:
                self.graph[zone1].append((zone2, self.connections[connection]))
            else:
                self.graph[zone1] = [(zone2, self.connections[connection])]
            if self.graph.get(zone2) is not None:
                self.graph[zone2].append((zone1, self.connections[connection]))
            else:
                self.graph[zone2] = [(zone1, self.connections[connection])]

    def advance_turn(self) -> str:
        """Advance one simulation turn and return the display output."""
        result: str = ""
        for drone in self.drones.values():

            # Skip drones that have already completed delivery.
            if drone.status == DroneStatus.DELIVERED:
                continue

            # Next zone the drone intends to move to.
            action: str = drone.path[0]

            # Restricted zones require special handling because the drone may
            # spend time in the intermediate connection before entering.
            if self.zones[action].type == ZoneType.RESTRICTED:
                if self._is_restricted_action_allowed(drone, action):
                    if isinstance(drone.loc, str):
                        self.zones[drone.loc].drones_inside_remove(drone)
                        x, y = tuple(sorted((drone.loc, action)))
                        drone.loc = (x, y)
                        self.connections[drone.loc].currently_trav_append(
                            drone)
                    else:
                        self.connections[
                            drone.loc].currently_traversing_remove(drone)
                        drone.loc = action
                        self.zones[action].drones_inside_append(drone)
                        drone.path = drone.path[1:]
                        if not drone.path:
                            drone.status = DroneStatus.DELIVERED

                    # Build the display output after the move.
                    if isinstance(drone.loc, str):
                        try:
                            result += f"{drone.id}-" + \
                                colored(f"{drone.loc} ",
                                        self.zones[action].color)
                        except KeyError:
                            # default color
                            result += f"{drone.id}-" + \
                                colored(f"{drone.loc} ", "red")
                    else:
                        try:
                            result += f"{drone.id}-" + \
                                colored(f"{drone.loc[0]}-{drone.loc[1]} ",
                                        self.zones[action].color)
                        except KeyError:
                            result += f"{drone.id}-" + \
                                colored(
                                    f"{drone.loc[0]}-{drone.loc[1]} ", "blue")
                continue

            # Normal movement: the drone can
            # move directly into the target zone.
            if self._is_action_allowed(drone, action):
                old_loc: str | Tuple[str, str] = drone.loc
                drone.loc = action
                drone.path = drone.path[1:]
                if not drone.path:
                    drone.status = DroneStatus.DELIVERED
                self.zones[action].drones_inside_append(drone)
                if isinstance(old_loc, str):
                    # Move the drone out of its previous zone and into the
                    # connecting link so traversal capacity is tracked.
                    self.zones[old_loc].drones_inside_remove(drone)
                    x, y = tuple(sorted((old_loc, action)))
                    self.connections[(x, y)].currently_trav_append(drone)
                try:
                    result += f"{drone.id}-" + colored(
                        f"{drone.loc} ",
                        self.zones[action].color
                    )
                except KeyError:
                    result += f"{drone.id}-" + colored(
                        f"{drone.loc} ",
                        "green"
                    )
        # Clean up any drones that finished traversing the connection
        # and are now in a normal or priority zone.
        for connection in self.connections.values():
            if connection.currently_traversing:
                for drone in connection.currently_traversing:
                    if (
                            isinstance(drone.loc, str) and (
                                self.zones[drone.loc].type in [
                                    ZoneType.NORMAL, ZoneType.PRIORITY])
                    ):
                        connection.currently_traversing_remove(drone)

        return result

    def all_delivered(self) -> bool:
        """Return True when every drone has completed its route."""
        for drone in self.drones.values():
            if drone.status != DroneStatus.DELIVERED:
                return False
        return True

    def update_drone_status(self, drone: Drone) -> None:
        """Update the drone status when its route is finished."""
        if not drone.path:
            drone.status = DroneStatus.DELIVERED

    def _is_action_allowed(self, drone: Drone, action: str) -> bool:
        """Return True if the drone can move into the requested zone."""
        src: str | Tuple[str, str] = drone.loc
        if not self.zones[action].is_available():
            return False
        # Determine the connection key for this move.
        a: str = ""
        b: str = ""
        if isinstance(src, str):
            a, b = sorted((src, action))
        key: tuple[str, str] = (a, b)
        if not self.connections[key].is_available():
            return False
        return True

    def _is_restricted_action_allowed(self, drone: Drone, action: str) -> bool:
        """Return True for valid restricted-zone moves."""
        if isinstance(drone.loc, tuple):
            # Drone is currently waiting in a
            # connection; any target move is allowed.
            return True

        # Otherwise, ensure the connection is
        # free before entering restricted zone.
        l1, l2 = tuple(sorted((drone.loc, action)))
        if self.connections[(l1, l2)].is_available():
            return True

        return False

    def validate_sorte_paths(
        self,
        solutions: List[List[str]]
    ) -> List[Tuple[str, ...]]:
        """Filter out invalid paths and score valid routes by cost."""
        filtered_solutions: Dict[Tuple[str, ...], int] = {}
        for path in solutions:
            valid_path: bool = True
            cost: int = len(path)
            # Blocked zones are invalid; restricted zones increase path cost.
            for zone_name in path:
                zone_type = self.zones[zone_name].type
                if zone_type == ZoneType.BLOCKED:
                    valid_path = False
                    break
                elif zone_type == ZoneType.RESTRICTED:
                    cost += 1
            if valid_path:
                filtered_solutions[tuple(path)] = cost
        return [path for path in dict(
            sorted(filtered_solutions.items(), key=lambda item: item[1]))]

    def sorte_by_priority(
        self,
        solutions: List[Tuple[str, ...]],
    ) -> List[Tuple[str, ...]]:
        """Sort solutions by the number of priority zones in each path."""
        return sorted(solutions, key=self._factor_calulator)

    def _factor_calulator(self, path: Tuple[str, ...]) -> int:
        """Return the number of priority zones in the given path."""
        factor: int = 0
        for zone_name in path:
            zone_type = self.zones[zone_name].type
            if zone_type == ZoneType.PRIORITY:
                factor += 1
        return factor
