#!/bin/bash

PATHS=(
  #"maps/easy/01_linear_path.txt"
  #"maps/easy/02_simple_fork.txt"
  #"maps/easy/03_basic_capacity.txt"

  #"maps/medium/01_dead_end_trap.txt"
  #"maps/medium/02_circular_loop.txt"
  #"maps/medium/03_priority_puzzle.txt"

  #"maps/hard/01_maze_nightmare.txt"
  #"maps/hard/02_capacity_hell.txt"
  #"maps/hard/03_ultimate_challenge.txt"

  "maps/challenger/01_the_impossible_dream.txt"
)

source venv/bin/activate
for script in "${PATHS[@]}"; do
  echo "running $script"
  python3 fly_in.py "$script"
  echo "------------"
done
#  maps/challenger:
#01_the_impossible_dream.txt

#maps/easy:
#01_linear_path.txt  02_simple_fork.txt  03_basic_capacity.txt
#
#maps/hard:
#01_maze_nightmare.txt 02_capacity_hell.txt 03_ultimate_challenge.txt
#
#maps/medium:
#01_dead_end_trap.txt 02_circular_loop.txt 03_priority_puzzle.txt
