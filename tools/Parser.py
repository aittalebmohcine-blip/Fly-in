from typing import List

from tools.Connection import Connection
from tools.Zone import Zone
from tools.Map import Map


class Parser():
    '''reads the file and instantiates Zone, Connection, and Drone objects.'''

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def parse(self) -> Map:
        map: Map = Map()

        # Logic to read file and return the Map object
        try:
            with open(self.file_path, "r") as file:
                errors: List[str] = []
                first_valid_line: bool = True
                start_hub_exist: bool = False
                end_hub_exist: bool = False
                nb_drones_exist: bool = False
                for lineno, line in enumerate(file, 1):
                    line.strip()
                    try:
                        if not line or line.startswith("#"):
                            continue
                        if ":" not in line:
                            raise ValueError("missing: ':")
                        prefix: str = line.split(":", 1)[0]
                        # first line is nb_drones
                        if first_valid_line:
                            if prefix != "nb_drones":
                                raise ValueError(
                                    "first valid line must be 'nb_drones'"
                                )
                            first_valid_line = False
                        # duplicat start, end hub or nb_drones
                        if prefix == "nb_drones":
                            if nb_drones_exist:
                                raise ValueError("Duplicate nb_drones line.")
                            map.nb_drones = self._parse_nb_drones(line)
                            nb_drones_exist = True
                        elif prefix == "start_hub":
                            if start_hub_exist:
                                raise ValueError("Duplicate start_hub.")
                            self._parse_hub(line)
                            start_hub_exist = True
                        elif prefix == "end_hub":
                            if end_hub_exist:
                                raise ValueError("Duplicate end_hub.")
                            self._parse_hub(line)
                            end_hub_exist = True
                        elif prefix == "hub":
                            self._parse_hub(line)
                        elif prefix == "connection":
                            self._parse_connection(line)
                    except Exception as e:
                        errors.append(f"Line {lineno}: {e}")
                    if errors:
                        raise ValueError("\n".join(errors))
            return map

        except FileNotFoundError:
            raise RuntimeError("Config file not found")
        except PermissionError:
            raise RuntimeError("Permission denied while reading config file")
        except IsADirectoryError as e:
            raise RuntimeError(e)

    @staticmethod
    def _parse_connection(line: str) -> Connection:
        ...

    @staticmethod
    def _parse_hub(line: str) -> Zone:
        ...

    @staticmethod
    def _parse_nb_drones(line: str):
        try:
            x: str = line.split(":", 1)[1]
            return int(x)
        except ValueError:
            raise ValueError("nb_drones must be an integer")
