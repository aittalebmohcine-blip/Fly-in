"""Zone data model used by the Fly_in simulation.

Each Zone tracks its coordinates, type, capacity, color, and the drones
currently inside it. The model exposes convenience methods for zone access.
"""
from typing import List
from pydantic import BaseModel


from tools.Definitions import Point, ZoneType, EdgeType
from tools.Drone import Drone


class Zone(BaseModel):
    '''Represents a physical location (Hub, Start, End, Restricted, etc.).
    Stores coordinates, type, capacity, current drones, and display color.'''

    coords: Point
    type: ZoneType
    edge: EdgeType
    capacity: int
    drones_inside: List[Drone]
    color: str

    def is_available(self) -> bool:
        """Return True when the zone can accept another drone."""
        return self.capacity > len(self.drones_inside)

    def drones_inside_append(self, drone: Drone) -> None:
        """Add a drone to the list of drones currently inside this zone."""
        self.drones_inside.append(drone)

    def drones_inside_remove(self, drone: Drone) -> None:
        """Remove a drone from the zone if it is currently present."""
        if drone in self.drones_inside:
            self.drones_inside.remove(drone)
