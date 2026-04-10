from typing import Optional, Tuple, List
from pydantic import BaseModel

from tools.Drone import Drone
from tools.Zone import Zone


class Connection(BaseModel):
    '''Represents the link between two zones.
    Responsibility:
    Know the two zones it connects,
    its max_link_capacity,and track drones currently
    traversing it (crucial for the 2-turn restricted movement rule).'''

    connecete: Tuple[Zone, Zone]
    max_link_capacity: int
    currently_traversing: Optional[List[Drone]]

    def is_available(self) -> bool:
        if self.currently_traversing is None:
            return True
        if self.max_link_capacity > len(self.currently_traversing):
            return True
        return False

    def currently_trav_append(self, drone: Drone) -> None:
        if not self.currently_traversing:
            self.currently_traversing = [drone]
            return
        self.currently_traversing.append(drone)

    def currently_traversing_remove(self, drone: Drone) -> None:
        if self.currently_traversing:
            self.currently_traversing.remove(drone)
