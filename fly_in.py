import copy
from typing import List, Tuple
from tools.Parser import Parser
from tools.Simulation import Simulation
import sys


def main() -> None:
    # handling arguments
    if len(sys.argv) != 2:
        print("usage: python3 fly_in.py <config-file>")
        exit(1)
    file_path = sys.argv[1]

    try:
        # parsing
        parser = Parser(file_path)
        map = parser.parse()

        # simulating
        map.build_graph()
        graph = map.graph
        solutions: List[List[str]] = Simulation.find_all_paths(
            graph, "start", "goal")

        # solve the graph
        valid_sorted: List[Tuple[str, ...]
                           ] = map.validate_sorte_paths(solutions)
        priority_sorted: List[Tuple[str, ...]
                              ] = map.sorte_by_priority(valid_sorted)
        # give eache drone a path based on priority
        i = 0
        for name, drone in map.drones.items():
            drone.path = copy.deepcopy(priority_sorted[i % map.nb_drones])

        # print("---initialization done, starting simulation...---\n")

        i = 0
        while not map.all_delivered():
            i += 1
            print(f"Turn {i}: ", map.advance_turn())

    except Exception as e:
        # print(e)
        raise e
        return

# try:
#    parser.parsing_config_file(file_path)
# except Exception as e:
#    print(e)
#    exit(1)


if __name__ == "__main__":
    main()
