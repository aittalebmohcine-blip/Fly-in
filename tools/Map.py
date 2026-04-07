from typing import Dict, Tuple
from pydantic import BaseModel

from tools.Drone import Drone
from tools.Connection import Connection
from tools.Zone import Zone
from tools.Definitions import DroneStatus


class Map(BaseModel):
    nb_drones: int = 0
    zones: Dict[str, Zone] = {}
    connections: Dict[Tuple[str, str], Connection] = {}
    drones: Dict[str, Drone] = {}
    graph: Dict[str, list[Tuple[str, Connection]]] = {}

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
            if drone.status == DroneStatus.DELIVERED:
                continue
            # - ask the drone what it wants to do
            action = drone.path[0]
            # ask the zone/connection if that action is allowed
            if self._is_action_allowed(drone, action):
                # - update the state
                # drone
                old_loc = drone.loc
                drone.loc = action  # stil have to handle restriced zones
                drone.path.pop(0)
                if drone.path == []:
                    drone.status = DroneStatus.DELIVERED
                # update taget zone and current zone
                self.zones[action].drones_inside_append(drone)
                self.zones[old_loc].drones_inside_remove(drone)
                # connection:
                #   this is related to the restricted zones
                #   we need to update the curently_traversing list
                #   of the Connection in the case of restricted
                #   zones, and remove the drone from it after 2 turns
                # result
                result += f"{drone.id}-{action} "
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
        src: str = drone.loc
        a, b = sorted((src, action))
        key = (a, b)

        # unavailable zone
        if not self.zones[action].is_available():
            return False
        # unavailable connection
        if not self.connections[key].is_available():
            return False
        return True
