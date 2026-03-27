# Read file
# Validate everything
# Build:
# zones
# connections
# Stop on error

file_path = "maps/easy/01_linear_path.txt"

with open(file_path, "r") as file:
    for line in file:
        if line.startswith("#"):
            continue
        else:
            print(line)
