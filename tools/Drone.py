from typing import Tuple
from tools.Definitions import DroneStatus
from pydantic import BaseModel


class Drone(BaseModel):
    '''Represents a single drone.
    Responsibility:
    Track its own ID, current location,
    status (moving, waiting, delivered), and path.
    It decides when to move based on its internal state.'''

    id: str
    # loc: Point
    loc: str | Tuple[str, str]  # zone name or a connection entry
    status: DroneStatus
    path: Tuple[str, ...] = ()
