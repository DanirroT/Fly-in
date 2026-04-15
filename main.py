

import sys

from input import read_map_file


def main(args: list[str]) -> None:

    # file_name = "maps/easy/01_linear_path.txt"
    if len(args) == 1:
        print("No Map Given. Try Again")
        return

    if len(args) != 2:
        print("Too many Arguments! Try Again")
        return
    file_name = args[1]
    try:
        drone_map = read_map_file(file_name)
    except FileNotFoundError as e:
        print(e)
        return
    except ValueError as e:
        print(f"Error reading map file: {e}")
        return
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return

    print()
    print("Drones", drone_map.nb_drones)
    print("Zones", len(drone_map.zones))
    print("Connections", len(drone_map.connections))

    print()

    print(drone_map.get_nice_summary())

    # drone_map.print_map()


if __name__ == "__main__":
    main(sys.argv)
