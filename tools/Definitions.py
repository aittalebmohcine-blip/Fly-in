from typing import Tuple
from enum import Enum

Point = Tuple[int, int]

print("hello")


class DroneStatus(Enum):
    MOVING = "moving"
    WAITING = "waiting"
    DELIVERED = "delivered"


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
