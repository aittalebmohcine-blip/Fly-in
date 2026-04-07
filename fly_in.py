import copy
from typing import List
from tools.Parser import Parser
from tools.Simulation import Simulation
from tools.Drone import Drone
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
        solution: List[str] = Simulation.find_the_shortest_path(
            graph, "start", "goal")
        drone: Drone
        for drone in map.drones.values():
            drone.path = copy.deepcopy(solution)
        print("---initialization done, starting simulation...---\n")
        i = 0
        while map.all_delivered() is False:
            i += 1
            print(map.advance_turn())
            if i > 10:
                print("simulation is taking too long, exiting...")
                exit(1)

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
