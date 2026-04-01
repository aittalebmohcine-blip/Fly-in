from tools.Network import Network


class Parser():
    '''reads the file and instantiates Zone, Connection, and Drone objects.'''

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def parse(self) -> Network:
        network: Network = Network()

        # Logic to read file and return the Map object
        try:
            with open(self.file_path, "r") as file:
                pass
            return network

        except FileNotFoundError:
            raise RuntimeError("Config file not found")
        except PermissionError:
            raise RuntimeError("Permission denied while reading config file")
        except IsADirectoryError as e:
            raise RuntimeError(e)

    @staticmethod
    def _parse_nb_drones(key: str, value: str):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{key} must be an integer (got '{value}')")
