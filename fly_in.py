from tools import parser
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python3 fly_in.py <config-file>")
        exit(1)

    file_path = sys.argv[1]
    try:
        parser.parsing_config_file(file_path)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
