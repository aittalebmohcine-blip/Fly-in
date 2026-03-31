from pydantic import BaseModel
from typing import List, Dict, Any, Tuple, Optional


def parse_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{key} must be an integer (got '{value}')")


def parse_coords(value: Tuple[str, str], key: str) -> Tuple[int, int]:
    x: int = parse_int(value[0], key)
    y: int = parse_int(value[1], key)
    return (x, y)


def remove_first_last(s: str) -> Optional[str]:
    return s[1:-1] if len(s) > 2 else None


DEFAULTS: Dict[str, Any] = {
    "zone": "normal",
    "color": None,
    "max_drones": 1,
}
ZONE_VALID_VALUES = ["normal", "blocked", "restricted", "priority"]


def parse_meta_data(value: str, key: str) -> Dict[str, Any]:
    if not value.startswith("[") or not value.endswith("]"):
        raise ValueError(
            "zone definition format should be: <name> <x> <y> [metadata]")
    v: List[str] = remove_first_last(value).split()
    data: str
    for data in v:
        result: Dict[str, str] = {}
        if "=" not in data:
            raise ValueError(f"missing '=' in {data}")
        paire = data.split("=")
        result[paire[0]] = paire[1]


def parse_hub(value: str, key: str) -> Dict[str, Any]:
    parts: List[str] = value.split(None, 3)
    if len(parts) < 3:
        raise ValueError(
            "zone definition format should be: <name> <x> <y> [metadata]")
    return {
        "hub_type": key,
        "name": parts[0],
        "coords": parse_coords((parts[1], parts[2]), key),
        "meta-data": (
            parse_meta_data(parts[3], key) if len(parts) == 4 else DEFAULTS
        )
    }


class DronesConfig(BaseModel):
    NB_DRONES: int
    START_HUB: str
    END_HUB: str
    HUBS: list[str]
    CONNECTIONS: list[str]


ALLOWED_KEYS = {"NB_DRONES", "START_HUB", "HUB", "END_HUB", "CONNECTION"}
META_DATA = {"ZONE", "COLOR", "MAX_DRONES", "MAX_LINK_CAPACITY"}


def parsing_config_file(file_path: str) -> DronesConfig:
    errors: List[str] = []
    raw: Dict[str, Any] = {}

    try:
        with open(file_path, "r") as file:

            lineno: int
            line: str
            first_valid_line: bool = True
            start_hub_exist: bool = False
            end_hub_exist: bool = False

            for lineno, line in enumerate(file, 1):
                # skip coments and impty lines
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                # invalid line
                if ":" not in line:
                    errors.append(f"Line {lineno}: missing ':'")
                    continue

                # split
                key: str
                value: str
                key, value = map(str.strip, line.split(":", 1))
                key = key.upper()

                # invalid key
                if key not in ALLOWED_KEYS:
                    errors.append(f"Line {lineno}: unknown key '{key}'")
                    continue

                # duplicated key
                # if key in raw:
                #    errors.append(f"Line {lineno}: duplicate key '{key}'")
                #    continue

                try:
                    # first line is nb_drones
                    if first_valid_line:
                        if key != "NB_DRONES":
                            raise ValueError(
                                "first valid line must be 'NB_DRONES'"
                            )
                        raw[key] = parse_int(value, key)
                        first_valid_line = False

                    # duplicat start or end hub
                    if key == "START_HUB" and start_hub_exist:
                        raise ValueError("Duplicate start_hub.")
                    if key == "END_HUB" and end_hub_exist:
                        raise ValueError("Duplicate end_hub.")
                    if key == "START_HUB":
                        start_hub_exist = True
                    elif key == "END_HUB":
                        end_hub_exist = True

                    # parse hubs: extract type, name, x, y,optional metadata
                    elif key in {"START_HUB", "HUB", "END_HUB"}:
                        zone: Dict[str, Any] = parse_hub(value, key)
                        if zone['name'] in raw:
                            errors.append(
                                f"Line {lineno}: duplicate name "
                                f"'{zone['name']}'"
                            )
                        raw[zone["name"]] = zone

                    # parse connections

                except ValueError as e:
                    errors.append(f"Line {lineno}: {e}")

            print(raw)
            if errors:
                raise ValueError("\n".join(errors))

            # return DronesConfig(**raw)

    except FileNotFoundError:
        raise RuntimeError("Config file not found")

    except PermissionError:
        raise RuntimeError("Permission denied while reading config file")


# Read file
# Validate everything
# Build:
#   - zones
#   - connections
# Stop on error
