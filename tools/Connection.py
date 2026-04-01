from typing import Tuple, List

from tools.Drone import Drone
from tools.Zone import Zone


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
