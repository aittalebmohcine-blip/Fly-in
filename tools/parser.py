from pydantic import BaseModel
from typing import List, Dict, Any, Tuple


def parse_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{key} must be an integer (got '{value}')")


def parse_coords(value: Tuple[str, str], key: str) -> Tuple[int, int]:
    x: int = parse_int(value[0], key)
    y: int = parse_int(value[1], key)
    return (x, y)


def parse_meta_data():
    pass


def parse_hub(value: str, key: str) -> Dict[str, Any]:
    parts: List[str] = value.split(3)
    return {
        "name": parts[0],
        "coords": parse_coords((parts[1], parts[2]), key),
        "meta-data": parse_meta_data(parts[3])
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
                if key in raw:
                    errors.append(f"Line {lineno}: duplicate key '{key}'")
                    continue

                try:
                    # first line is nb_drones
                    if first_valid_line:
                        if key != "NB_DRONES":
                            raise ValueError(
                                f"Line {lineno}: 1st line must be 'NB_DRONES'"
                            )
                        raw[key] = parse_int(value, key)
                        first_valid_line = False

                    # parse hubs
                    if key in {"START_HUB", "HUB", "END_HUB"}:
                        result: Dict[str, Any] = parse_hub(value, key)
                        raw[]

                    # parse connections

                except ValueError as e:
                    errors.append(f"Line {lineno}: {e}")

            if errors:
                raise ValueError("\n".join(errors))

            return DronesConfig(**raw)

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
