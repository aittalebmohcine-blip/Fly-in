"""Drone model for Fly_in.

Describes the individual drone state including ID, current location,
status, and route path.
"""
from typing import Tuple
from Definitions import DroneStatus
try:
    from pydantic import BaseModel
except ImportError:
    print("Error: 'pydantic' is not installed."
          " Please install it using 'pip install pydantic'.")
    exit(1)


class Drone(BaseModel):
    '''Represents a single drone and its current route state.'''

    id: str
    loc: str | Tuple[str, str]  # zone name or a connection entry
    status: DroneStatus
    path: Tuple[str, ...] = ()
