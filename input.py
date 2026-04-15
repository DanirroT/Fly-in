from typing import Any
import sys
from map_classes import Coordinates, DroneMap

from utils import str_to_dict_parse


def read_map_file(file_name: str) -> DroneMap | Any:

    with open(file_name) as file:
        file_str = file.read()

    file_lines = file_str.splitlines()

    nb_drones = 0
    zones: list[tuple[str, str, Coordinates, dict[str, str]]] = []
    connections: list[tuple[str, str, dict[str, str]]] = []

    i = 0
    while file_lines[i].startswith("#") or not file_lines[i].strip():
        i += 1

    print(file_lines[i])

    if not file_lines[i].startswith("nb_drones:"):
        raise ValueError("First line must define 'nb_drones'")

    for line in file_lines:
        line = line.split("#")[0].strip()
        if not line:
            continue

        elif line.startswith("nb_drones:"):
            if not nb_drones:
                nb_drones = int(line.split(":")[1].strip())
            else:
                raise ValueError("Multiple definitions of 'nb_drones'")

        elif line.startswith(("start_hub:", "hub:", "end_hub:")):
            hub_type: str = ""
            rest: str = ""
            name: str = ""
            x: str = ""
            y: str = ""

            metadata: list[str] = []
            try:
                hub_type, rest = line.split(":", 1)
                name, x, y, *metadata = rest.split()
                if metadata:
                    metadata[0] = metadata[0][1:]
                    metadata[-1] = metadata[-1][:-1]
                    meta_dict = str_to_dict_parse(" ".join(metadata), " ", "=")
                else:
                    meta_dict = {}
                zones.append((hub_type, name,
                              Coordinates(int(x), int(y)),
                              meta_dict))
            except ValueError as e:
                raise ValueError(
                    f"Line not according to Zone Format\n{line}\n"
                    "Zone Formatting must be\n"
                    f"<hub_type>: <name> <x> <y> [metadata]\n{e}")

        elif line.startswith("connection:"):
            a: str = ""
            b: str = ""
            metadata: list[str] = []

            try:
                _, conn = line.split(":")
                a, pre_b = conn.strip().split("-")
                b, *metadata = pre_b.split()
                if metadata:
                    if metadata[0][:1] != "[":
                        raise ValueError(
                            "Metadata must be in between Square Brackets\nor\n"
                            f"Detected Junk Data at the end of line\n{line}")
                    if metadata[-1][-1:] != "]":
                        raise ValueError(
                            "Metadata must be in between Square Brackets\nor\n"
                            f"Detected Junk Data at the end of line\n{line}")
                    # metadata[0] = metadata[0][:-1]
                    # metadata[-1] = metadata[-1][1:]
                    meta_dict = str_to_dict_parse(" ".join(metadata), " ", "=")
                else:
                    meta_dict = {}

                connections.append((a, b, meta_dict))
            except ValueError as e:
                raise ValueError(
                    f"Line not according to Connection Format\n{line}\n"
                    "Connection Formatting must be\n"
                    f"connection: <name1>-<name2> [metadata]\n{e}")

        else:
            raise ValueError(
                f"Line not according to Any Format\n{line}\n"
            )

    return DroneMap(nb_drones, zones, connections)  # type: ignore
    # return nb_drones, zones, connections


if __name__ == "__main__":

    args = sys.argv

    # file_name = "maps/easy/01_linear_path.txt"
    if len(args) == 1:
        print("No Map Given. Try Again")
        sys.exit()

    if len(args) != 2:
        print("Too many Arguments! Try Again")
        sys.exit()
    file_name = args[1]
    drone_map = read_map_file(file_name)

    print()
    print("Drones", drone_map.nb_drones)
    print("Zones", len(drone_map.zones))
    print("Connections", len(drone_map.connections))

    print()

    # print(drone_map.get_summary())

    print(drone_map.get_nice_summary())
