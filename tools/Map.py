try:
    from termcolor import colored
except ImportError:
    print("Error: 'termcolor' is not installed."
          " Please install it using 'pip termcolor pydantic'.")
    exit(1)
from pydantic import BaseModel

from typing import Dict, Tuple, List

from tools.Drone import Drone
from tools.Connection import Connection
from tools.Zone import Zone
from tools.Definitions import DroneStatus, ZoneType, EdgeType


class Map(BaseModel):
    nb_drones: int = 0
    zones: Dict[str, Zone] = {}
    connections: Dict[Tuple[str, str], Connection] = {}
    drones: Dict[str, Drone] = {}
    graph: Dict[str, list[Tuple[str, Connection]]] = {}

    def verify_start_goal_in_graph(self) -> None:
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
        start: str = ""
        goal: str = ""
        for zone in self.zones:
            if self.zones[zone].edge == EdgeType.START:
                start = zone
            if self.zones[zone].edge == EdgeType.END:
                goal = zone
        return (start, goal)

    @staticmethod
    def verify_solutions(
        solutions: List[List[str]],
        start: str,
        goal: str
    ) -> None:
        for solution in solutions:
            if solution[0] == start and solution[-1] == goal:
                return
        raise RuntimeError(
            "GRAPH ERROR: make sure there is a link between start and end hubs"
        )

    def build_graph(self) -> None:
        connection: tuple[str, str]
        zone1: str
        zone2: str

        for connection in self.connections:
            zone1, zone2 = connection
            if self.graph.get(zone1) is not None:
                self.graph[zone1].append((zone2, self.connections[connection]))
            else:
                self.graph[zone1] = [(zone2, self.connections[connection])]
            if self.graph.get(zone2) is not None:
                self.graph[zone2].append((zone1, self.connections[connection]))
            else:
                self.graph[zone2] = [(zone1, self.connections[connection])]

    def advance_turn(self) -> str:
        result = ""
        for drone in self.drones.values():

            # skip arrived drones
            if drone.status == DroneStatus.DELIVERED:
                continue

            # - ask the drone what it wants to do
            action = drone.path[0]

            # restricted action handling
            if self.zones[action].type == ZoneType.RESTRICTED:
                if self._is_restricted_action_allowed(drone, action):
                    # update zone link, and connection state
                    # drone in a zone => move it to the Connection
                    if isinstance(drone.loc, str):
                        self.zones[drone.loc].drones_inside_remove(drone)
                        x, y = tuple(sorted((drone.loc, action)))
                        drone.loc = (x, y)
                        self.connections[drone.loc].currently_trav_append(
                            drone)
                    # drone in a Connection => move it the zone
                    else:
                        self.connections[
                            drone.loc
                        ].currently_traversing_remove(drone)

                        drone.loc = action
                        self.zones[action].drones_inside_append(drone)
                        drone.path = drone.path[1:]
                        if not drone.path:
                            drone.status = DroneStatus.DELIVERED
                        # stor conection
                        # old_loc = drone.loc
                        # drone.loc = action
                        # drone.path = drone.path[1:]
                        # if not drone.path:
                        #    drone.status = DroneStatus.DELIVERED
                        # update taget zone and current zone
                        # self.connections[old_loc].currently_traversing_remove(
                        #    drone)
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

            # normal action handling
            # ask the zone/connection if that action is allowed
            if self._is_action_allowed(drone, action):
                # - update the state
                # drone
                old_loc = drone.loc
                drone.loc = action  # stil have to handle restriced zones
                drone.path = drone.path[1:]
                if not drone.path:
                    drone.status = DroneStatus.DELIVERED
                # update taget zone and current zone
                self.zones[action].drones_inside_append(drone)
                if isinstance(old_loc, str):
                    self.zones[old_loc].drones_inside_remove(drone)
                    x, y = tuple(sorted((old_loc, action)))
                    self.connections[(x, y)].currently_trav_append(
                        drone)
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
        for drone in self.drones.values():
            if drone.status != DroneStatus.DELIVERED:
                return False
        return True

    def update_drone_status(self, drone: Drone) -> None:
        if not drone.path:
            drone.status = DroneStatus.DELIVERED

    def _is_action_allowed(self, drone: Drone, action: str) -> bool:
        src: str | Tuple[str, str] = drone.loc

        # unavailable zone
        if not self.zones[action].is_available():
            return False
        # unavailable connection
        a: str = ""
        b: str = ""
        if isinstance(src, str):
            a, b = sorted((src, action))
        key = (a, b)
        if not self.connections[key].is_available():
            return False
        return True

    def _is_restricted_action_allowed(self, drone: Drone, action: str) -> bool:
        # - if the drone is waiting in a connection and the target zone is
        #   free then the action is valid
        if isinstance(drone.loc, tuple):
            # if not self.zones[drone.loc[1]].is_available():
            #    raise ValueError(
            #        "trying to move to an inavailable restricted zone")
            return True
        # - if the drone in a zone and the connection is free
        #   the action is allowed
        l1, l2 = tuple(sorted((drone.loc, action)))
        if self.connections[(l1, l2)].is_available():
            return True
        return False

    def validate_sorte_paths(

        self,
        solutions: List[List[str]]

    ) -> List[Tuple[str, ...]]:

        filtered_solutions: Dict[Tuple[str, ...], int] = {}
        cost: int

        # remove paths with blocked zones
        for path in solutions:
            valid_path: bool = True
            cost = len(path)
            for zone in path:
                type = self.zones[zone].type
                if type == ZoneType.BLOCKED:
                    valid_path = False
                    break
                elif type == ZoneType.RESTRICTED:
                    cost += 1
            if valid_path:
                filtered_solutions[tuple(path)] = cost
        # sort and return
        return [path for path in dict(
            sorted(filtered_solutions.items(), key=lambda item: item[1]))]

    def sorte_by_priority(

        self,
        solutions: List[Tuple[str, ...]],

    ) -> List[Tuple[str, ...]]:
        """sorts the given list of paths by the number of zones
        who they have a priority type"""

        return sorted(solutions, key=self._factor_calulator)

    def _factor_calulator(self, path: Tuple[str, ...]) -> int:
        """returns the count of priority zones in the given path"""
        factor: int = 0
        for zone in path:
            type = self.zones[zone].type
            if type == ZoneType.PRIORITY:
                factor += 1
        return factor
