"""Connection model for Fly_in.

Tracks the link between two zones, its capacity, and the drones currently
moving through the connection.
"""
from typing import Optional, Tuple, List
from pydantic import BaseModel

from Drone import Drone
from Zone import Zone


class Connection(BaseModel):
    '''Represents the link between two zones.
    Stores max capacity and the drones currently traversing the link.'''

    connecete: Tuple[Zone, Zone]
    max_link_capacity: int
    currently_traversing: Optional[List[Drone]]

    def is_available(self) -> bool:
        """Return True when the connection has room for another drone."""
        if self.currently_traversing is None:
            return True
        # Compare current occupancy against the configured capacity.
        return self.max_link_capacity > len(self.currently_traversing)

    def currently_trav_append(self, drone: Drone) -> None:
        """Add a drone to the connection traversal list."""
        if not self.currently_traversing:
            self.currently_traversing = [drone]
            return
        # Append the drone if the connection already has active traversals.
        self.currently_traversing.append(drone)

    def currently_traversing_remove(self, drone: Drone) -> None:
        """Remove a drone from the connection traversal list."""
        if self.currently_traversing:
            self.currently_traversing.remove(drone)
