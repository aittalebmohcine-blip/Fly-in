from Definitions import Point, ZoneType
from Drone import Drone


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
