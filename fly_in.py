from typing import List, Tuple
import sys
import copy


from tools.Parser import Parser
from tools.Simulation import Simulation


def main() -> None:

    # handling arguments
    if len(sys.argv) != 2:
        print("usage: python3 fly_in.py <config-file>")
        exit(1)
    file_path = sys.argv[1]

    try:
        # creat the parser object
        parser = Parser(file_path)

        # file is empty
        if parser.is_empty_stat():
            raise RuntimeError("ERROR: Empty config file !")

        # build the map obj
        map = parser.parse()

        # building the graph
        map.build_graph()
        graph = map.graph

        # extract start and gola zone names
        start, goal = map.extract_start_goal_names()

        # start: str = ""
        # goal: str = ""
        # for zone in map.zones:
        #    if map.zones[zone].edge == EdgeType.START:
        #        start = zone
        #    if map.zones[zone].edge == EdgeType.END:
        #        goal = zone

        # graph has start and goal nodes
        map.verify_start_goal_in_graph()
        # s_exist: bool = False
        # g_exist: bool = False
        # for node in graph.keys():
        #    if node == start:
        #        s_exist = True
        #    elif node == goal:
        #        g_exist = True
        # if not all((s_exist, g_exist)):
        #    raise RuntimeError(
        #        "GRAPH ERROR: make sure there is a "
        #        "link between start and end hubs")

        # find all possible paths
        solutions: List[List[str]] = Simulation.find_all_paths(
            graph, start, goal)

        # verify at least one solution exist
        map.verify_solutions(solutions, start, goal)
        # prepare solutions for use by removing start from theme.
        # since all dronces begins at start
        Simulation.remove_start_from_solutions(solutions)

        # validate and sorte the paths based on theire priority
        valid_sorted: List[Tuple[str, ...]
                           ] = map.validate_sorte_paths(solutions)
        priority_sorted: List[Tuple[str, ...]
                              ] = map.sorte_by_priority(valid_sorted)

        # give eache drone a path based on priority
        i = 0
        for _, drone in map.drones.items():
            drone.path = copy.deepcopy(priority_sorted[i % map.nb_drones])

        # start the simulation
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
