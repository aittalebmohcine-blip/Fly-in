from typing import Tuple

from Definitions import Point, DroneStatus


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
