from typing import List, Tuple
import sys
import copy


from Parser import Parser
from Simulation import Simulation


def main() -> None:

    # Validate command-line arguments and pick the config file path.
    if len(sys.argv) != 2:
        print("usage: python3 fly_in.py <config-file>")
        exit(1)
    file_path = sys.argv[1]

    try:
        # Create the parser instance for the provided config file.
        parser = Parser(file_path)

        # Ensure the config file is not empty before parsing.
        if parser.is_empty_stat():
            raise RuntimeError("ERROR: Empty config file !")

        # Build the internal map from zones, connections, and drones.
        map = parser.parse()

        # Convert connection definitions into an adjacency graph.
        map.build_graph()
        graph = map.graph

        # Find the special start and goal hubs for routing.
        start, goal = map.extract_start_goal_names()

        # give all drones start as the init loc
        map.init_drones_at_start(start)

        # Ensure the graph contains both the start and goal nodes.
        map.verify_start_goal_in_graph()

        # Discover every possible path from start to goal.
        solutions: List[List[str]] = Simulation.find_all_paths(
            graph, start, goal)

        # Confirm that at least one valid solution exists.
        map.verify_solutions(solutions, start, goal)
        # Remove the start node from every route because drones
        # are already positioned at the start hub.
        Simulation.remove_start_from_solutions(solutions)

        # Validate routes and sort them by cost and priority.
        valid_sorted: List[Tuple[str, ...]
                           ] = map.validate_sorte_paths(solutions)
        # Raise an error if there is no valid paths
        if not valid_sorted:
            raise RuntimeError(
                "GRAPH ERROR: make sure there is"
                " a link between start and end hubs"
            )
        priority_sorted: List[Tuple[str, ...]
                              ] = map.sorte_by_priority(valid_sorted)

        # Assign each drone a route.
        for drone in map.drones.values():
            drone.path = copy.deepcopy(
                priority_sorted[0]
            )

        # Begin simulation output after initialization completes.
        print("---initialization done, starting simulation...---\n")

        i = 0
        # Advance the simulation until every drone has delivered.
        while not map.all_delivered():
            i += 1
            print(f"Turn {i}: ", map.advance_turn())

    except Exception as e:
        # Print any runtime or parsing failure messages.
        print(e)
        return


# Run the main function when executed as a script.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation interrupted! quitting.")
