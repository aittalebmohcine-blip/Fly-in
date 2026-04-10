from typing import List
from pydantic import BaseModel


from tools.Definitions import Point, ZoneType
from tools.Drone import Drone


class Zone(BaseModel):
    '''Represents a physical location (Hub, Start, End, Restricted, etc.).
    Responsibility:
    Know its coordinates,
    type (normal/blocked/restricted/priority),
    capacity limits (max_drones),
    and which drones are currently inside it.
    It validates if a drone can enter.'''

    coords: Point
    type: ZoneType
    capacity: int
    drones_inside: List[Drone]
    color: str

    def is_available(self) -> bool:
        if self.capacity - len(self.drones_inside) > 0:
            return True
        return False

    # func to append a drone
    def drones_inside_append(self, drone: Drone) -> None:
        self.drones_inside.append(drone)

    # func to remove a drone
    def drones_inside_remove(self, drone: Drone) -> None:
        if drone in self.drones_inside:
            self.drones_inside.remove(drone)
