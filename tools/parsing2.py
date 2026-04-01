# from abc import ABC, abstractmethod

# Parser: Create a Parser class that reads the file and
# instantiates Zone, Connection, and Drone objects.

from typing import Tuple, List
from enum import Enum

Point = Tuple[int, int]


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
    '''Represents a single drone.
    Responsibility:
    Track its own ID, current location,
    status (moving, waiting, delivered), and path.
    It decides when to move based on its internal state.'''

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
    '''Represents a physical location (Hub, Start, End, Restricted, etc.).
    Responsibility:
    Know its coordinates,
    type (normal/blocked/restricted/priority),
    capacity limits (max_drones),
    and which drones are currently inside it.
    It validates if a drone can enter.'''

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
    '''Represents the link between two zones.
    Responsibility:
    Know the two zones it connects,
    its max_link_capacity,and track drones currently
    traversing it (crucial for the 2-turn restricted movement rule).'''

    def __init__(self) -> None:
        self.connecete: Tuple[Zone, Zone]
        self.max_link_capacity: int
        self.currently_traversing: List[Drone]


class Network():
    '''The container for all Zones and Connections.
    Responsibility:
    Parse the input file, build the graph,
    and provide methods to find neighbors or calculate path costs.'''
    pass


class Simulation():
    '''The conductor of the system.
    Responsibility:
    Manage the "Turn" loop.
    It asks every Drone what it wants to do,
    asks every Zone/Connection if that action is allowed,
    updates the state, and prints the output.'''
    pass
