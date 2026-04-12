from typing import Any
from map_classes import Coordinates, DroneMap


def read_map_file(file_name: str) -> DroneMap | Any:

    with open(file_name) as file:
        file_str = file.read()

    file_lines = file_str.splitlines()

    nb_drones = 0
    zones: list[tuple[str, str, Coordinates, list[str]]] = []
    connections: list[tuple[str, str, list[str]]] = []

    for line in file_lines:
        line = line.split("#")[0].strip()
        if not line:
            continue

        elif line.startswith("nb_drones:"):
            if not nb_drones:
                nb_drones = int(line.split(":")[1].strip())
            else:
                raise ValueError("Multiple defenitions of 'nb_drones'")

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
                zones.append((hub_type, name,
                              Coordinates(int(x), int(y)),
                              metadata))
            except ValueError as e:
                raise ValueError(
                    f"Line not acording to Zone Format\n{line}\n"
                    "Zone Formating must be\n"
                    f"<hub_type>: <name> <x> <y> [metadata]\n{e}")

        elif line.startswith("connection:"):
            a: str = ""
            b: str = ""
            metadata: list[str] = []

            try:
                _, conn = line.split(":")
                a, pre_b = conn.strip().split("-")
                b, *metadata = pre_b.split()

                connections.append((a, b, metadata))
            except ValueError as e:
                raise ValueError(
                    f"Line not acording to Connection Format\n{line}\n"
                    "Connection Formating must be\n"
                    f"connection: <name1>-<name2> [metadata]\n{e}")

        else:
            raise ValueError(
                f"Line not acording to Any Format\n{line}\n"
            )

    return DroneMap(nb_drones, zones, connections)
    # return nb_drones, zones, connections


if __name__ == "__main__":

    file_name = "maps/easy/01_linear_path.txt"
    drone_map = read_map_file(file_name)
    # print("\n".join(map(str, drone_map)))
    print(drone_map.nb_drones)
    print(len(drone_map.zones))
    print(len(drone_map.connections))
