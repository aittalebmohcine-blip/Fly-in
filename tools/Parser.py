from typing import List, Any, Dict

from tools.Drone import Drone
from tools.Connection import Connection
from tools.Zone import Zone
from tools.Definitions import DroneStatus, Point, ZoneMetadataKeys, ZoneType
# from tools.Map import Map


class Parser():
    '''reads the file and instantiates Zone, Connection, and Drone objects.'''

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def parse(self):
        # map: Map = Map()
        config: Dict[Any, Any] = {}

        # Logic to read file and return the Map object
        try:
            with open(self.file_path, "r") as file:
                errors: List[str] = []
                first_valid_line: bool = True
                start_hub_exist: bool = False
                end_hub_exist: bool = False
                nb_drones_exist: bool = False
                nb_drones: int = 0
                zone_lines: Dict[int, str] = {}

                line: str
                for lineno, line in enumerate(file, 1):
                    line = line.strip()
                    try:
                        if not line or line.startswith("#"):
                            continue
                        if ":" not in line:
                            raise ValueError("missing ':'")
                        prefix: str = line.split(":", 1)[0].strip()
                        # first line is nb_drones
                        if first_valid_line:
                            first_valid_line = False
                            if prefix != "nb_drones":
                                raise ValueError(
                                    "first valid line must be 'nb_drones'"
                                )
                        # duplicat start, end hub or nb_drones
                        if prefix == "nb_drones":
                            if nb_drones_exist:
                                raise ValueError("Duplicate nb_drones line.")
                            nb_drones: int = self._parse_nb_drones(line)
                            nb_drones_exist = True
                        elif prefix == "start_hub":
                            if start_hub_exist:
                                raise ValueError("Duplicate start_hub.")
                            zone_lines[lineno] = line
                            start_hub_exist = True
                        elif prefix == "end_hub":
                            if end_hub_exist:
                                raise ValueError("Duplicate end_hub.")
                            zone_lines[lineno] = line
                            end_hub_exist = True
                        elif prefix == "hub":
                            zone_lines[lineno] = line
                        elif prefix == "connection":
                            self._parse_connection(line)
                        else:
                            raise ValueError(f"Unknown key '{prefix}'")
                    except Exception as e:
                        errors.append(f"Line {lineno}: {e}")
                # missing start or end zone
                for err in self._start_end_zones_existstance(
                        start_hub_exist, end_hub_exist):
                    errors.append(err)
                if errors:
                    raise ValueError("\n".join(errors))

            config["nb_drones"] = nb_drones
            config["zones"] = self._zones_factory(zone_lines)
            config["connections"] = ...
            config["drones"] = self._drones_factory(nb_drones)
            # return map

        except FileNotFoundError:
            raise RuntimeError("Config file not found")
        except PermissionError:
            raise RuntimeError("Permission denied while reading config file")
        except IsADirectoryError as e:
            raise RuntimeError(e)

    def _zones_factory(self, data: Dict[int, str]) -> Dict[str, Zone]:
        zone: Zone
        space: Dict[str, Zone] = {}
        line: str
        for lineno, line in data.items():
            # remove the prefix
            line = line.split(":")[1].strip()
            # split and strip
            l: List[str] = list(map(str.strip, line.split(None, 3)))
            # validate format
            if len(l) < 3:
                raise ValueError(
                    "Invalid zone! use '<zone>: <name> <x> <y> [metadata]'")
            coords: Point = self._parse_coords(l[1], l[2])
            if len(l) == 4:
                metadata: Dict[str, Any] = self._parse_zone_metadata(
                    l[3], lineno)
            zone = ...
        return space

    @staticmethod
    def _parse_zone_metadata(metadata: str, lineno: int) -> Dict[ZoneMetadataKeys, Any]:
        error_msg = f"Line {lineno}: Invalid metadata format. example usage '[type=zone]' (3 key value paires at most)"
        # default metadata
        result: Dict[ZoneMetadataKeys, Any] = {
            ZoneMetadataKeys.COLOR: None,
            ZoneMetadataKeys.ZONE: ZoneType.NORMAL,
            ZoneMetadataKeys.MAX_DRONES: 1,
        }
        key_existe: dict[ZoneMetadataKeys, bool] = {
            ZoneMetadataKeys.ZONE: False,
            ZoneMetadataKeys.COLOR: False,
            ZoneMetadataKeys.MAX_DRONES: False,
        }
        #           # defining validators
        #           k: str
        #           v: str
        #           validators = {
        #               ZoneMetadataKeys.ZONE: lambda v: ZoneType(v),
        #               ZoneMetadataKeys.COLOR: lambda v: isinstance(v, str) and len(v.split()) == 1,
        #               ZoneMetadataKeys.MAX_DRONES: lambda v: isinstance(
        #                   v, int) and v >= 1,
        #           }
        # validate format
        if not all((metadata.startswith("["), metadata.endswith("]"))):
            raise ValueError(error_msg)
        # error on '=' invalid count
        counter: int = metadata.count("=")
        if (not counter and metadata) or counter > 3:
            raise ValueError(error_msg)
        # get the row format
        metadata = metadata[1:-1]
        # sub validation func

        def validate_kv(k: str, v: str) -> None:
            # udates parent func vars if k,v are valid else raises error
            nonlocal key_existe
            nonlocal result
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
                value = ZoneType(v)
            elif key == ZoneMetadataKeys.COLOR:
                value = v
            elif key == ZoneMetadataKeys.MAX_DRONES:
                # check if max_drones is a positive integer
                if not v.isdigit() or int(v) < 1:
                    raise ValueError(
                        f"Line {lineno}: max_drones must be an integer >= 1")
                else:
                    value = int(v)
            result[key] = value

        def split_at_indices(target: List, split_indices: List[int]) -> List[str]:
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
            kvs: List[str] = list(map(str.strip, metadata.split("=", 3)))
            kvs = split_at_indices(kvs, [1, 2])
            if len(kvs) != 6:
                raise ValueError(error_msg)
            validate_kv(*kvs[:2])
            validate_kv(*kvs[2:4])
            validate_kv(*kvs[4:])
        print(result)
        return result

    @ staticmethod
    def _parse_coords(x: int, y: int) -> Point:
        try:
            return (int(x), int(y))
        except Exception:
            raise ValueError("Could not parse coordinates")

    @ staticmethod
    def _drones_factory(count: int) -> Dict[str, Drone]:
        swarm: Dict[str, Drone] = {}
        name: str
        for x in range(count):
            name = f"D{x}"
            drone: Drone = Drone(
                id=name,
                loc=(0, 0),
                status=DroneStatus.WAITING,
            )
            swarm[name] = drone
        return swarm

    @ staticmethod
    def _start_end_zones_existstance(start: bool, end: bool):
        if not start:
            yield ("There must be exactly one start_hub: zone ")
        if not end:
            yield ("There must be exactly one end_hub: zone ")

    @ staticmethod
    def _parse_connection(line: str) -> Connection:
        ...

    @ staticmethod
    def _parse_hub(line: str) -> Zone:
        ...

    @ staticmethod
    def _parse_nb_drones(line: str):
        try:
            x: str = line.split(":", 1)[1]
            return int(x)
        except ValueError:
            raise ValueError("nb_drones must be an integer")
