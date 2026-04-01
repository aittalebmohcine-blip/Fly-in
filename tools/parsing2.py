# from abc import ABC, abstractmethod

# Parser: Create a Parser class that reads the file and
# instantiates Zone, Connection, and Drone objects.

from typing import Tuple, List
from enum import Enum

Point = tuple[int, int]


class DroneStatus(Enum):
    MOVING = "moving"
    WAITING = "waiting"
    DELIVERED = "delivered"


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Drone():
    '''It decides when to move based on its internal state.'''

    def __init__(
            self,
            id: str,
            loc: Tuple[int, int],
            status: DroneStatus,
            path: str,
    ) -> None:
        self.id: str = id
        self.loc: Point = loc
        self.status: DroneStatus = status
        self.path: str = path


class Zone():
    def __init__(
            self,
            coords: Point,
            type: ZoneType,
            capacity: int,
            drones_inside: Drone,
    ) -> None:
        self.coords: Point = coords
        self.type: ZoneType = type
        self.capacity: int = capacity
        self.drones_inside: Drone = drones_inside


class Connection():
    def __init__(self) -> None:
        self.connecete: Tuple[Zone, Zone]
        self.max_link_capacity: int
        self.currently_traversing: List[Drone]
