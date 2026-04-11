import copy
from typing import List, Tuple
from tools.Definitions import EdgeType
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

        start: str = ""
        end: str = ""
        for zone in map.zones:
            if map.zones[zone].edge == EdgeType.START:
                start = zone
            if map.zones[zone].edge == EdgeType.END:
                end = zone
        solutions: List[List[str]] = Simulation.find_all_paths(
            graph, start, end)

        # solve the graph
        valid_sorted: List[Tuple[str, ...]
                           ] = map.validate_sorte_paths(solutions)
        priority_sorted: List[Tuple[str, ...]
                              ] = map.sorte_by_priority(valid_sorted)
        # give eache drone a path based on priority
        i = 0
        for _, drone in map.drones.items():
            drone.path = copy.deepcopy(priority_sorted[i % map.nb_drones])

        print("---initialization done, starting simulation...---\n")

        i = 0
        while not map.all_delivered():
            i += 1
            print(f"Turn {i}: ", map.advance_turn())

    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation interrupted! quitting.")
