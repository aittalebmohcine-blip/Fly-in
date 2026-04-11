from typing import Tuple
from enum import Enum

Point = Tuple[int, int]


class DroneStatus(Enum):
    MOVING = "moving"
    WAITING = "waiting"
    DELIVERED = "delivered"


class ZoneMetadataKeys(Enum):
    ZONE = "zone"  # (default: normal)
    COLOR = "color"  # (default: none)
    MAX_DRONES = "max_drones"  # (default: 1)


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class EdgeType(Enum):
    START = "start"
    END = "end"
    NONE = None
