from typing import List, Any, Dict, Tuple, Iterator
import os

from tools.Drone import Drone
from tools.Connection import Connection
from tools.Zone import Zone
from tools.Definitions import (
    DroneStatus, EdgeType, Point, ZoneMetadataKeys, ZoneType)
from tools.Map import Map


class Parser():
    '''reads the file and instantiates Zone, Connection, and Drone objects.'''

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def is_empty_stat(self) -> bool:
        return os.stat(self.file_path).st_size == 0

    def parse(self) -> Map:
        # map: Map = Map()
        config: Dict[Any, Any] = {}

        # Logic to read file and return the Map object
        try:
            # opening the file
            with open(self.file_path, "r") as file:
                errors: List[str] = []
                first_valid_line: bool = True
                start_hub_exist: bool = False
                end_hub_exist: bool = False
                nb_drones_exist: bool = False
                connection_exist: bool = False
                nb_drones: int = 0
                zone_lines: Dict[int, str] = {}
                connection_lines: Dict[int, str] = {}

                line: str
                # reading line by line
                for lineno, line in enumerate(file, 1):
                    line = line.strip()
                    try:
                        # remove comments
                        if not line or line.startswith("#"):
                            continue
                        if "#" in line:
                            line = line.split("#", 1)[0].strip()

                        # missig ':'
                        if ":" not in line:
                            raise ValueError("missing ':'")

                        # pick the prefix
                        prefix: str = line.split(":", 1)[0].strip()

                        # - first time to reache this block, means
                        # first valid line is true
                        # - first line is nb_drones
                        if first_valid_line:
                            first_valid_line = False
                            if prefix != "nb_drones":
                                # beffor raising an error, validate that line
                                if prefix == "start_hub":
                                    start_hub_exist = True
                                if prefix == "end_hub":
                                    end_hub_exist = True
                                raise ValueError(
                                    "first valid line must be 'nb_drones'"
                                )

                        # duplicat start, end hub or nb_drones
                        # - check duplicate nb_drones. parse it.
                        if prefix == "nb_drones":
                            if nb_drones_exist:
                                raise ValueError("Duplicate nb_drones line.")
                            nb_drones = self._parse_nb_drones(line)
                            nb_drones_exist = True

                        # - check duplicate nb_drones.
                        elif prefix == "start_hub":
                            if start_hub_exist:
                                raise ValueError("Duplicate start_hub.")
                            zone_lines[lineno] = line
                            start_hub_exist = True

                        # - check duplicate nb_drones.
                        elif prefix == "end_hub":
                            if end_hub_exist:
                                raise ValueError("Duplicate end_hub.")
                            zone_lines[lineno] = line
                            end_hub_exist = True

                        # add hub to zone_lines dict
                        elif prefix == "hub":
                            zone_lines[lineno] = line
                        # add connection to connection_lines
                        elif prefix == "connection":
                            connection_exist = True
                            connection_lines[lineno] = line

                        # error on an unkoun key.
                        else:
                            raise ValueError(f"Unknown key '{prefix}'")

                    # catch and save errors.
                    except Exception as e:
                        errors.append(f"Line {lineno}: {e}")

                # missing start or end zone
                for err in self._start_end_connec_existstance(
                        start_hub_exist, end_hub_exist, connection_exist):
                    errors.append(err)
                if errors:
                    raise ValueError("\n".join(errors))

            config["nb_drones"] = nb_drones
            config["zones"] = self._zones_factory(zone_lines, nb_drones)
            config["drones"] = self._drones_factory(nb_drones)
            config["connections"] = self._connection_factory(
                connection_lines, config["zones"])
            return Map(**config)

        except FileNotFoundError:
            raise RuntimeError("Config file not found")
        except PermissionError:
            raise RuntimeError("Permission denied while reading config file")
        except IsADirectoryError as e:
            raise RuntimeError(e)

    def _zones_factory(
        self,
        data: Dict[int, str],
        nb_drones: int
    ) -> Dict[str, Zone]:

        zone: Zone
        space: Dict[str, Zone] = {}
        line: str
        raw_names: List[str] = []
        for lineno, line in data.items():

            # remove the prefix
            line_suf = line.split(":")[1].strip()

            # split and strip
            l: List[str] = list(map(str.strip, line_suf.split(None, 3)))

            # empty zone data
            if not l:
                raise ValueError(
                    f"Line {lineno}: Invalid zone! "
                    "use '<zone>: <name> <x> <y> [metadata]'")

            # make sure there is no '-' in the name
            if "-" in l[0]:
                raise ValueError(
                    f"Line {lineno}: '-' is not allowed in the zone name")

            # make sure name does not exists and add it to raw names
            if l[0] in raw_names:
                raise ValueError(f"Line {lineno}: duplicated zone name")
            raw_names.append(l[0])

            # validate format
            if len(l) < 3:
                raise ValueError(
                    f"Line {lineno}: Invalid zone! "
                    "use '<zone>: <name> <x> <y> [metadata]'")
            try:
                coords: Point = self._parse_coords(l[1], l[2])
            except ValueError as e:
                raise ValueError(f"Line {lineno}: {e}")

            metadata: Dict[
                str,
                Any
            ] = self._parse_zone_metadata(l[3] if len(l) == 4 else "", lineno)

            zone = Zone(coords=coords, **metadata)
            # make sure end_hub and start_hub have capacity equal to nb_drones
            # and the type is start/end
            prefix: str = line.split(":")[0].strip()
            if prefix in {"end_hub", "start_hub"}:
                zone.capacity = nb_drones
                if prefix == "start_hub":
                    zone.edge = EdgeType.START
                if prefix == "end_hub":
                    zone.edge = EdgeType.END
            space[l[0]] = zone
        return space

    @staticmethod
    def _drones_factory(count: int) -> Dict[str, Drone]:
        swarm: Dict[str, Drone] = {}
        name: str
        for x in range(count):
            name = f"D{x}"
            drone: Drone = Drone(
                id=name,
                loc="start",
                status=DroneStatus.WAITING,
            )
            swarm[name] = drone
        return swarm

    def _connection_factory(
            self,
            data: Dict[int, str],
            zones: Dict[str, Zone]
    ) -> Dict[Tuple[str, str], Connection]:

        error_msg = "Invalid connection! use "
        error_msg += "'connection: <name1>-<name2> [metadata]'"
        connections: Dict[Tuple[str, str], Connection] = {}
        names: Tuple[str, str]
        raw: List[Tuple[str, str]] = []

        for lineno, line in data.items():

            # remove the prefix
            line = line.split(":", 1)[1].strip()
            if not line:
                raise ValueError(f"Line {lineno}: {error_msg}")

            # split and strip
            l: List[str] = list(map(str.strip, line.split(None, 1)))

            # validate conection format
            # "-" in connection name
            if "-" not in l[0]:
                raise ValueError(error_msg)

            # get the two zone names and ensure they are stripped
            z1, z2 = tuple(map(str.strip, l[0].split("-", 1)))
            names = (z1, z2)
            if z1 == z2:
                raise ValueError(
                    f"Line {lineno}: self-referencing connection not allowed"
                )

            # ensure order is consistent for undirected connection
            names = (names[0], names[1]) if names[0] < names[1] else (
                names[1], names[0])
            if names in raw:
                raise ValueError(
                    f"Line {lineno}: Duplicate connection "
                    f"'{names[0]}-{names[1]}'")
            raw.append(names)
            # are names valid zone names
            if not set(names).issubset(set(zones)):
                raise ValueError(
                    f"Line {lineno}: Connection names must be valid zone names"
                )
            # build the connection tuple
            connecte = (zones[names[0]], zones[names[1]])

            # verify metadata if exists and build the connection object
            x: int = 1
            if len(l) == 2 and l[1]:  # if metadata exists and is not empty

                # verify brackets exitance
                if not l[1].startswith("[") or not l[1].endswith("]"):
                    raise ValueError(f"Line {lineno}: {error_msg}")

                # rmove brackets and strip
                l[1] = l[1][1:-1].strip()

                # error on multiple '=' signe
                if l[1].count("=") != 1:
                    raise ValueError(
                        f"Line {lineno}: Connection metadata must "
                        "contain exactly one key-value pair"
                    )

                # metadata must start with max_link_capacity
                key: str
                value: str
                key, value = list(map(str.strip, l[1].split("=", 1)))
                if key != "max_link_capacity":
                    raise ValueError(
                        f"Line {lineno}: Wrong metadata key! "
                        "only 'max_link_capacity' is allowed"
                    )

                # parse the capacity value
                x = self._parse_connection_metadata(value, lineno)

            # create the connection obj
            connection: Connection = Connection(
                connecete=connecte,
                max_link_capacity=x,
                currently_traversing=[]
            )
            connections[names] = connection
        return connections

    @staticmethod
    def _parse_connection_metadata(data: str, i: int) -> int:
        try:
            x: int = int(data)
            if x < 1:
                raise ValueError()
            return x
        except ValueError:
            raise ValueError(
                f"Line {i}: max_link_capacity must be a valid integer >= 1")

    @staticmethod
    def _parse_zone_metadata(
            metadata: str,
            lineno: int
    ) -> Dict[str, Any]:
        error_msg = f"Line {lineno}: Invalid metadata format. "
        error_msg += "example usage '[type=zone]' (3 key value paires at most)"
        # default metadata
        result: Dict[str, Any] = {
            "type": ZoneType.NORMAL,
            "capacity": 1,
            "drones_inside": [],
            "color": "white",
            "edge": None
        }
        # if metadata is empty, return default
        if not metadata:
            return result

        key_existe: dict[ZoneMetadataKeys, bool] = {
            ZoneMetadataKeys.ZONE: False,
            ZoneMetadataKeys.COLOR: False,
            ZoneMetadataKeys.MAX_DRONES: False,
        }
        if not all((metadata.startswith("["), metadata.endswith("]"))):
            raise ValueError(error_msg)
        if metadata.count("[") > 1 or metadata.count("]") > 1:
            raise ValueError(error_msg)
        # error on '=' invalid count
        counter: int = metadata.count("=")
        if (not counter and metadata) or counter > 3:
            raise ValueError(error_msg)
        # remove first and last brackets
        metadata = metadata[1:-1]
        # sub validation func

        def validate_kv(k: str, v: str) -> None:
            # ensure k and v are not empty
            if not k or not v:
                raise ValueError(error_msg)
            # udates parent func vars if k,v are valid else raises error
            # nonlocal key_existe
            # nonlocal result
            # get the enum key
            try:
                key = ZoneMetadataKeys(k)
            except ValueError:
                raise ValueError(f"Line {lineno}: Unkown key '{k}'")
            # ensure key is not duplicated
            if key_existe[key]:
                raise ValueError(f"Line {lineno}: Duplicated key '{k}'")
            key_existe[key] = True
            # ensure value is valid and update result
            value: Any = v
            if key == ZoneMetadataKeys.ZONE:
                # raises an error if v is not valid zone type
                k = "type"  # zone type is represented as type in Zone class
                value = ZoneType(v)
            elif key == ZoneMetadataKeys.COLOR:
                if "-" in v or " " in v:
                    raise ValueError(
                        f"Line {lineno}: color must be a single word "
                        "without spaces or dashes"
                    )
                value = v
            elif key == ZoneMetadataKeys.MAX_DRONES:
                # check if max_drones is a positive integer
                if not v.isdigit() or int(v) < 1:
                    raise ValueError(
                        f"Line {lineno}: max_drones must be an integer >= 1")
                else:
                    value = int(v)
                    # k is max_drones but i store it as capacity
                    k = "capacity"
            result[k] = value
            # print(result.keys())

        def split_at_indices(
                target: List[str],
                split_indices: List[int]
        ) -> List[str]:
            tokens: List[str] = []
            for i, item in enumerate(target):
                if i in split_indices:
                    tokens.extend(item.split(None, 1))
                else:
                    tokens.append(item)
            return tokens

        # only one "="
        if counter == 1:
            kv: List[str] = list(map(str.strip, metadata.split("=", 1)))
            if len(kv) != 2:
                raise ValueError(error_msg)
            validate_kv(*kv)
        if counter == 2:
            kvs: List[str] = list(map(str.strip, metadata.split("=", 2)))
            kvs = split_at_indices(kvs, [1])
            if len(kvs) != 4:
                raise ValueError(error_msg)
            validate_kv(*kvs[:2])
            validate_kv(*kvs[2:])
        if counter == 3:
            kvs = list(map(str.strip, metadata.split("=", 3)))
            kvs = split_at_indices(kvs, [1, 2])
            if len(kvs) != 6:
                raise ValueError(error_msg)
            validate_kv(*kvs[:2])
            validate_kv(*kvs[2:4])
            validate_kv(*kvs[4:])
        return result

    @staticmethod
    def _parse_coords(x: str, y: str) -> Point:
        try:
            return (int(x), int(y))
        except Exception:
            raise ValueError("Could not parse coordinates.")

    @staticmethod
    def _parse_nb_drones(line: str) -> int:
        try:
            x: str = line.split(":", 1)[1]
            if int(x) < 1:
                raise ValueError()
            return int(x)
        except ValueError:
            raise ValueError("nb_drones must be an integer >= 1")

    @staticmethod
    def _start_end_connec_existstance(
        start: bool,
        end: bool,
        conn: bool
    ) -> Iterator[str]:
        if not start:
            yield ("There must be exactly one start_hub: zone ")
        if not end:
            yield ("There must be exactly one end_hub: zone ")
        if not conn:
            yield ("There must be at least one connection")
