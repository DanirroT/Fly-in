import re


def main():
    file_str = """

    # Easy Level 1: Simple linear path
    nb_drones: 2

    start_hub: start 0 0 [color=green]
    hub: waypoint1 1 0 [color=blue]
    hub: waypoint2 2 0 [color=blue]
    end_hub: goal 3 0 [color=red]

    connection: start-waypoint1
    connection: waypoint1-waypoint2
    connection: waypoint2-goal

    """

    file_lines = file_str.splitlines()

    file_lines_ncomments = [line.split("#")[0].strip() for line in file_lines]

    seachable = "\n".join(file_lines_ncomments).strip()

    print("seachable\n\n", seachable)

    nb_drones_seach = re.findall(r"nb_drones:\s(\d+)", seachable)
    nb_hubs_seach = re.findall(r"(start_hub|hub|end_hub):\s([A-Za-z1-9]+)\s(\d+)\s(\d+)", seachable)
    nb_connections_seach = re.findall(r"connection:\s([A-Za-z1-9]+)-([A-Za-z1-9]+)", seachable)

    # if not nb_drones_seach or not nb_hubs_seach or not nb_connections_seach:
    #     return

    print("1", nb_drones_seach)
    if len(nb_drones_seach) != 1:
        raise ValueError("Multiple defenitions of 'nb_drones'")
    print()

    print(nb_hubs_seach)
    print()

    print(nb_connections_seach)
    print()


if __name__ == "__main__":
    main()
