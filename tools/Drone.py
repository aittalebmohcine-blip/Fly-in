from re import I
from typing import Tuple
from tools.Definitions import DroneStatus
try:
    from pydantic import BaseModel
except ImportError:
    print("Error: 'pydantic' is not installed."
          " Please install it using 'pip install pydantic'.")
    exit(1)


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
