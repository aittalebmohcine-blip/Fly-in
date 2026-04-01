from typing import Dict
from pydantic import BaseModel

from tools.Definitions import Point
from tools.Drone import Drone
from tools.Connection import Connection
from tools.Zone import Zone


class Map(BaseModel):
    nb_drones: int
    zones: Dict[str, Zone]
    connections: Dict[Point, Connection]
    drones: Dict[str, Drone]
