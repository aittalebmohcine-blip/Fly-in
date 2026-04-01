from tools.Parser import Parser
import sys


def main() -> None:
    # handling arguments
    if len(sys.argv) != 2:
        print("usage: python3 fly_in.py <config-file>")
        exit(1)
    file_path = sys.argv[1]

    # parsing
    parser = Parser(file_path)
    try:
        map = parser.parse()
        print(map.nb_drones)
    except Exception as e:
        print(e)
        return

# try:
#    parser.parsing_config_file(file_path)
# except Exception as e:
#    print(e)
#    exit(1)


if __name__ == "__main__":
    main()
