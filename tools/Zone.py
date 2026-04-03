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
