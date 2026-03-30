from pydantic import BaseModel
from typing import List, Dict, Any


def pars_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{key} must be an integer (got '{value}')")


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
                # ---------------
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if ":" not in line:
                    errors.append(f"Line {lineno}: missing ':'")
                    continue

                key: str
                value: str
                key, value = map(str.strip, line.split(":", 1))
                key = key.upper()

                if key not in ALLOWED_KEYS:
                    errors.append(f"Line {lineno}: unknown key '{key}'")
                    continue

                if key in raw:
                    errors.append(f"Line {lineno}: duplicate key '{key}'")
                    continue
                # ---------------
                try:
                    if first_valid_line:
                        if key != "NB_DRONES":
                            raise ValueError(
                                f"Line {lineno}: 1st line must be 'NB_DRONES'"
                            )
                        raw[key] = pars_int(value, key)
                        first_valid_line = False
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
