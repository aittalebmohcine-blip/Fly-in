from tools.Definitions import Point, DroneStatus
from pydantic import BaseModel


class Drone(BaseModel):
    '''Represents a single drone.
    Responsibility:
    Track its own ID, current location,
    status (moving, waiting, delivered), and path.
    It decides when to move based on its internal state.'''

    id: str
    loc: Point
    status: DroneStatus
    path: str
