

import sys
from pydantic import ValidationError

from input import read_map_file
from drone_class import DroneManager
from visualizer import TerminalVisualizer, WindowedVisualizer
from validation_error_handling import error_processing


def terminal_clear() -> None:
    print("\033[H\033[J", end="")


def main(args: list[str]) -> None:

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
    except ValidationError as e:
        error_processing(e.errors())
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

    drone_map.print_map()

    input()

    terminal_clear()

    manager = DroneManager(drone_map, TerminalVisualizer())

    print(manager, len(manager.drones))

    print([zone.name for zone in manager.usable_zones])

    print()

    manager.drone_map.print_map()


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("The program has been forcefully stopped")
