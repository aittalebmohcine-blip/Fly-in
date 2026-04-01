from typing import Dict

from tools.Definitions import Point
from tools.Drone import Drone
from tools.Connection import Connection
from tools.Zone import Zone


class Map():
    def __init__(self) -> None:
        self.nb_drones: int
        self.zones: Dict[str, Zone]
        self.connections: Dict[Point, Connection]
        self.drones: Dict[str, Drone]
