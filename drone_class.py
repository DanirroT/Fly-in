import sys

from map_classes import Connection, DroneMap, Zone, ZoneType, Hubs
from visualizer import WindowedVisualizer
from visualizer import terminal_clear
# from time import sleep
from typing import Type


class DroneManager():
    drones: list["Drone"]
    drone_map: DroneMap
    usable_zones: set[Zone]
    visualizer: WindowedVisualizer
    turn: int = 0

    def __init__(self, drone_map: DroneMap,
                 visualizer: Type[WindowedVisualizer]
                 ) -> None:
        self.drone_map = drone_map

        self.visualizer = visualizer(self.drone_map)

        self.drones = [Drone(i, self.drone_map.start_zone)
                       for i in range(self.drone_map.nb_drones)]
        self.usable_zones = set([zone for zone in self.drone_map.zones
                                 if zone.zone != ZoneType.BLOCKED
                                 and zone.hub_type != Hubs.START_HUB])

        self.drone_map.start_zone.update_occupancy(self.drone_map.nb_drones)

    def dijkstra_zones(self) -> dict[Zone, tuple[int, int]]:
        pq: list[tuple[int, Zone]] = [(0, self.drone_map.end_zone)]

        dist: dict[Zone, tuple[int, int]] = {zone: (sys.maxsize, 0)
                                             for zone in self.drone_map.zones}
        visited: set[Zone] = set()
        dist[self.drone_map.end_zone] = (0, 0)

        self.drone_map.print_map()
        # print()
        # print()
        # print([str(zone) for _dict in pq for zone in _dict.values()])
        # print()
        # print("\n".join([f"{str(zone)}: {val}"
        #                  for zone, val in dist.items()]))
        # print()
        # print()

        while pq:
            pq.sort(key=lambda x: x[0])
            current_weight, current_zone = pq.pop(0)
            # print(current_weight, current_zone)
            if current_zone in visited:
                continue
            visited.add(current_zone)
            for conn, _ in current_zone.get_connections().items():
                weight = sys.maxsize
                if (conn.zone == ZoneType.NORMAL or
                        conn.zone == ZoneType.PRIORITY):
                    weight = 1
                if conn.zone == ZoneType.RESTRICTED:
                    weight = 2

                new_dist = current_weight + weight
                new_priority = (
                    dist[current_zone][1]
                    + int(conn.zone is ZoneType.PRIORITY)
                )

                if (
                    new_dist < dist[conn][0]
                    or (
                        new_dist == dist[conn][0]
                        and new_priority > dist[conn][1]
                    )
                ):
                    dist[conn] = (new_dist, new_priority)
                    # print("\t\t", conn, "is priority")
                pq.append((dist[conn][0], conn))
            # print([str(zone) for _dict in pq for zone in _dict.values()])
            # print()
            # print("\n".join([f"{str(zone)}: {val}"
            #                  for zone, val in dist.items()]))
            # print()
            # print()

        # print()
        # print("Final Dist:\n")

        # print("\n".join([f"{zone} : {vals}" for zone, vals in dist.items()]))
        # print()
        # print()

        sorted_dist = sorted(dist.items(), key=lambda item: item[1])

        print("\n".join([f"{zone} : {vals}" for zone, vals in sorted_dist]))

        return dist

    def build_priority_moves(self, dist: dict[Zone, tuple[int, int]]
                             ) -> dict[Zone, list[Zone]]:

        priority_moves: dict[Zone, list[Zone]] = {}

        for zone in self.drone_map.zones:

            neighbors = list(zone.get_connections())

            if self.drone_map.end_zone in neighbors:
                neighbors = [self.drone_map.end_zone]

            if self.drone_map.start_zone in neighbors:
                neighbors.remove(self.drone_map.start_zone)

            print(list(map(str, neighbors)))

            print(dist[zone])

            neighbors.sort(
                key=lambda n: (
                    -(dist[n][0]),
                    -(dist[n][1]),
                    n.max_drones
                )
            )
            print()
            print(list(map(str, neighbors)))

            input()

            priority_moves[zone] = neighbors

        return priority_moves

    def simulate_turn(
        self,
        priority_moves: dict[Zone, list[Zone]]
    ) -> str:

        # reserved: dict[Zone, int] = {}

        moved: str = "N/A"

        conn_occupancy: dict[Connection, int] = {}

        for drone in self.drones:

            print(drone)

            if drone.clear_buff():
                moved = "Buffer" + str(drone)
                continue

            if drone.loc == self.drone_map.end_zone:
                continue

            possible_moves = priority_moves[drone.loc]

            print(possible_moves)

            for zone in possible_moves:

                if zone == drone.last_zone:
                    continue

                zone_occupancy = (zone.get_occupancy())

                move_conn: Connection | None = None

                for conn in self.drone_map.connections:
                    if ((conn.start == drone.loc and conn.end == zone) or
                        (conn.end == drone.loc and conn.start == zone)):

                        move_conn = conn
                        conn_occupancy[move_conn] = conn_occupancy.get(move_conn, 0) + 1
                        break

                if move_conn is None:
                    raise TypeError(
                        f"Connection not found between {drone.loc} and {zone}"
                    )

                print(f"\t to {zone} {zone_occupancy}/{zone.max_drones} by",
                      f"{move_conn} {conn_occupancy[move_conn]}/{move_conn.max_link_capacity}")

                if (zone_occupancy >= zone.max_drones
                    or conn_occupancy[move_conn] >= move_conn.max_link_capacity):
                    continue

                # reserved[zone] = reserved.get(zone, 0) + 1

                # print("reserved:",
                #       " ".join([f"{zone.name}: {occ}"
                #                for zone, occ in reserved.items()]))

                print(
                    f"Drone {drone.index} moving "
                    f"{drone.loc.name} -> {zone.name}"
                )

                drone.move_to_zone(zone)
                moved = "Moved" + str(drone)

                print(drone.loc, drone.loc.get_occupancy())

                break
            input()
        return moved

    def calc_drone_pos(self) -> list[list[Zone]]:

        dijkstra_zone = self.dijkstra_zones()

        priority_moves = self.build_priority_moves(dijkstra_zone)

        # any_cleared = True

        # while any_cleared:
        #     any_cleared = False
        #     to_remove: list[Zone] = []

        #     for zone, neighbors in priority_moves.items():
        #         if (len(neighbors) == 1
        #             and zone.hub_type != Hubs.START_HUB
        #                 and zone.hub_type != Hubs.END_HUB):
        #             to_remove.append(zone)

        #     for doomed in to_remove:

        #         priority_moves[doomed] = []

        #         for zone, neighbors in priority_moves.items():

        #             if doomed in neighbors:
        #                 neighbors.remove(doomed)

        #         any_cleared = True

        #         print("cleared", doomed)

        # print()
        # print(self.drone_map.grid[1][7], priority_moves[self.drone_map.grid[1][7]])
        # print()

        # for zones in priority_moves:
        #     priority_moves[zones] = priority_moves[zones][:2]

        # print("priority")
        # print("\n\n".join([f"{str(zone)}: {"\n\t\t".join(map(str, val))}"
        #                   for zone, val in priority_moves.items()]))
        # print()

        pos_history: list[list[Zone]] = []

        turn = 1

        while True:

            pos_history.append([drone.loc for drone in self.drones])

            if all(
                drone.loc == self.drone_map.end_zone
                for drone in self.drones
            ):
                break

            print()
            print()
            print("turn:", turn)
            turn += 1

            moved = self.simulate_turn(priority_moves)

            # if moved == "N/A":
                # raise TabError(f"DEADLOCK {moved}")

            # input()

        return pos_history

    def run_program(self) -> None:
        import pygame
        print("Start Sim")
        self.visualizer.screen.blit(self.visualizer.background, (0, 0))

        input()
        terminal_clear()

        turn_list_output = self.calc_drone_pos()
        turns = len(turn_list_output)

        for drone in self.drones:
            # print(drone.index, end=" ")
            drone.loc = self.drone_map.start_zone
            # print("Back home")

        for zone in self.drone_map.zones:
            # print(zone, "," ,zone.get_occupancy(), end=" ")
            zone.zero_occupancy()
            # print("Back to", zone.get_occupancy())
        self.drone_map.start_zone.update_occupancy(self.drone_map.nb_drones)
        # print()
        # print("Zone Path:", [zone for zone in zone_path])
        # print()
        # print("Cap Path:", cap_path)

        # print()
        # print(f"turn_list_output: size: {turns}\n",
        #       "\n\n".join("\n".join(map(str, turn_list))
        #                   for turn_list in turn_list_output))

        run = True
        self.turn = 0

        self.visualizer.update_display(self.turn, turn_list_output[self.turn])
        print()
        print()
        print()
        control: bool = False
        while run:
            for event in pygame.event.get():

                # if event.type == pygame.MOUSEBUTTONDOWN:
                #     print(event)
                #     print()

                if (event.type == pygame.QUIT):
                    run = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL:
                        control = False

                if event.type == pygame.KEYDOWN:
                    print()
                    if event.key == pygame.K_LCTRL:
                        control = True
                    if ((event.key in (pygame.K_ESCAPE, pygame.K_q))):
                        run = False
                    if (control and event.key == pygame.K_c):
                        raise KeyboardInterrupt
                    if (event.key == pygame.K_LEFT) and self.turn - 1 >= 0:

                        self.turn -= 1
                        self.visualizer.update_display(
                            self.turn, turn_list_output[self.turn])
                        print("Turn backward -", self.turn)

                    if (event.key == pygame.K_RIGHT and
                            turns > self.turn + 1):

                        self.turn += 1
                        self.visualizer.update_display(
                            self.turn, turn_list_output[self.turn])
                        print("Turn forward -", self.turn)

                if event.type == pygame.VIDEORESIZE:
                    # print("VIDEORESIZE", event.w, event.h)
                    # print()
                    self.visualizer.resize(event.w, event.h, self.turn,
                                           turn_list_output[self.turn])

                elif event.type == pygame.WINDOWSIZECHANGED:
                    # print("WINDOWSIZECHANGED", event.x, event.y)
                    self.visualizer.resize(event.x, event.y, self.turn,
                                           turn_list_output[self.turn])

        print("Quit")

        print()
        print()
        self.visualizer.terminate()

    """

        current_zone = self.drone_map.end_zone
        return_path: list[Zone] = [current_zone]

        while current_zone != self.drone_map.start_zone:
            current_zone = min(current_zone.get_connections(),
                               key=lambda c: (dist[c][0], -dist[c][1]))
            return_path.append(current_zone)
            # print()
            # print()
            # print('current_zone', current_zone, dist[current_zone])

        return return_path[::-1]

    def get_cap_path(self, path: list[Zone]) -> list[int]:

        conns = self.drone_map.connections
        return_list: list[int] = []

        for i in range(len(path) - 1):

            # print(path[i].name, path[i+1].name)
            conn_cap = 0
            for conn in conns:
                if ((conn.start == path[i].name and
                     conn.end == path[i + 1].name) or
                    (conn.end == path[i].name and
                     conn.start == path[i + 1].name)):
                    conn_cap = conn.max_link_capacity
                    # print(f"Connection capacity between {path[i].name}\
                    #         and {path[i + 1].name}: {conn_cap}")
                    break
            zone_cap = path[i + 1].max_drones
            # print(f"Zone capacity of {path[i + 1].name}: {zone_cap}")
            if not conn_cap:
                raise TypeError(
                    "while building path, a capacity was not detected")
            return_list.append(min(conn_cap, zone_cap))

        return return_list

    def calc_drone_pos(self, zone_path: list[Zone], cap_path: list[int]
                       ) -> list[list[Zone]]:
        turn_list_output: list[list[Zone]] = [[self.drone_map.start_zone]
                                              * self.drone_map.nb_drones]
        drone_list: list[Drone] = self.drones.copy()
        turn = 0
        while drone_list:
            append_list: list[Zone] = []
            # print(list(map(str, drone_list)))
            for drone in drone_list.copy():
                if drone.clear_buff():
                    continue

                current_index = zone_path.index(drone.loc)

                next_zone = zone_path[current_index + 1]
                if (next_zone in drone.loc.get_connections() and
                        next_zone.max_drones - next_zone.get_occupancy() > 0):
                    drone.move_to_zone(next_zone)
                    # print(
                    #     f"Drone {drone.index} moved forward to",
                    #     f"{next_zone.name} with capacity",
                    #     f"{next_zone.get_occupancy()}/{next_zone.max_drones}")

                if drone.loc == self.drone_map.end_zone:
                    drone_list.remove(drone)

            for drone in self.drones:
                append_list.append(drone.loc)
                if drone.loc == self.drone_map.end_zone:
                    # print("Finished!")
                    continue
                # print(drone.loc.name, "  \t", drone.loc.loc,
                #       "\t", drone.loc.get_occupancy())
            # print()
            # print()
            # print("\n - ".join(map(str, append_list)))
            # print()
            # print()
            turn_list_output.append(append_list)
            turn += 1
        # print(turn_list_output)
        return turn_list_output
    """

    """
        for drone in self.drones:
            print(drone.loc, drone.loc.get_occupancy())
        print()
        while (self.drone_map.end_zone.get_occupancy()
               < self.drone_map.nb_drones):
            sleep(0.5)
            self.sim_turn()
            print()
            print()
            print("Turn:", self.turn)
            for drone in self.drones:
                if drone.loc == self.drone_map.end_zone:
                    print("Finished!")
                    continue
                print(drone.loc.name, "  \t", drone.loc.loc,
                      "\t", drone.loc.get_occupancy())
            print()


    def sim_turn(self) -> None:
        # connections = drone.loc.get_connections()
        for drone in self.drones:
            if drone.clear_buff():
                continue
            if drone.loc is self.drone_map.end_zone:
                continue

            drone_dest: Zone | None = None

            for _ in range(3):
                drone_dest = drone.make_decision(self.usable_zones)
                if (drone_dest and
                    (not (drone_dest.max_drones - drone_dest.get_occupancy() or
                     drone.loc.get_connections()[drone_dest]))):
                    drone_dest = None
                if drone_dest:
                    break

            if drone_dest:
                drone.move_to_zone(drone_dest)

        self.turn += 1

    """

    """
        dests: list[Zone] = [
            None for _ in range(self.drone_map.nb_drones)]  # type: ignore

        for drone in self.drones:
            if drone.buffer:
                drone.clear_buff()
                continue
            dests[drone.index] = drone.make_decision(self.usable_zones)
            if dests[drone.index] == drone.last_zone:
                self.usable_zones.pop(self.usable_zones.index(drone.loc))

        retry = [dests.index(unusable) for unusable in dests
                 if unusable not in self.usable_zones]
        empty_spots: dict[Zone, int] = {}
        for dest in self.usable_zones:
            empty_spots[dest] = dest.max_drones - dest.get_occupancy()
        for _ in range(self.turn + 1):
            while retry:
                for i in retry:
                    dests[i] = self.drones[i].make_decision(self.usable_zones)
                    if dests[i] == self.drones[i].last_zone:
                        self.usable_zones.pop(
                            self.usable_zones.index(self.drones[i].loc))
                retry = [dests.index(unusable) for unusable in dests
                         if unusable not in self.usable_zones]

            unique_dests: dict[Zone, int] = {dest: dests.count(dest)
                                             for dest in dests}
            full: set[Zone] = set()
            for dest, count in unique_dests.items():
                empty_spots_instance: int = empty_spots[dest]
                if empty_spots_instance >= count:
                    empty_spots_instance = count
                for dest_list in dests:
                    if dest_list == dest and empty_spots_instance > 0:
                        empty_spots_instance -= 1
                    else:
                        retry.append(dests.index(dest_list))
                        full.update([dest_list])
        self.turn += 1
        """

    """
    def turn_back(self, zone_path: list[Zone], cap_path: list[int]) -> None:
        # moved_to: dict[Zone, int] = {zone:  for zone in self.drone_map.zones}
        for drone in self.drones[::-1]:
            if drone.buffer:
                drone.buffer = None
                continue
            if drone.loc == self.drone_map.start_zone:
                continue

            current_index = zone_path.index(drone.loc)

            next_zone = zone_path[current_index - 1]
            if (next_zone in drone.loc.get_connections() and
                    next_zone.max_drones - next_zone.get_occupancy() > 0):
                drone.move_to_zone(next_zone)
                print(
                    f"Drone {drone.index} moved back to {next_zone.name}",
                    "with capacity",
                    f"{next_zone.get_occupancy()}/{next_zone.max_drones}")

        for drone in self.drones:
            if drone.loc == self.drone_map.end_zone:
                print("Finished!")
                continue
            print(drone.loc.name, "  \t", drone.loc.loc,
                  "\t", drone.loc.get_occupancy())
        # self.visualizer.animate_turn()

        self.turn -= 1
        print("Turn Back -", self.turn)
    """


class Drone():
    last_zone: Zone
    loc: Zone
    buffer: Zone | None
    index: int

    def __init__(self, index: int, start: Zone) -> None:
        self.index = index
        self.loc = start
        self.last_zone = start
        self.buffer = None

    def make_decision(self, zones_list: list[Zone]) -> Zone | None:

        for next_zone in zones_list:

            if self.loc.hub_type is Hubs.END_HUB:
                return None

            if (next_zone == self.last_zone or
                    next_zone.hub_type == Hubs.START_HUB):
                continue

            # if next_zone.get_occupancy() == next_zone.max_drones:
            #     continue

            return next_zone

        return None

    """
    def make_decision(self, usable_zones: set[Zone] | None = None) -> Zone:
        normal_zones: list[Zone] = []
        priority_zones: list[Zone] = []
        restricted_zones: list[Zone] = []
        zone_connections: dict[Zone, int] = self.loc.get_connections()
        if usable_zones is None:
            usable_zones = set([zone for zone in zone_connections
                                if (zone.zone != ZoneType.BLOCKED
                                    and zone.hub_type != Hubs.START_HUB)])
        if len(zone_connections) == 1:
            return list(zone_connections.keys())[0]
        non_back: dict[Zone, int] = {
            zone: cap for zone, cap in zone_connections.items()
            if zone != self.last_zone}
        if len(non_back) == 1:
            return list(non_back.keys())[0]
        for zone in non_back.keys():
            if zone.hub_type == Hubs.END_HUB:
                return zone
            if (zone not in usable_zones or
                    not zone.max_drones - zone.get_occupancy()):
                continue
            elif zone.zone == ZoneType.NORMAL:
                normal_zones.append(zone)
            elif zone.zone == ZoneType.PRIORITY:
                priority_zones.append(zone)
            elif zone.zone == ZoneType.RESTRICTED:
                restricted_zones.append(zone)

        if not any((priority_zones, normal_zones, restricted_zones)):
            return self.last_zone

        priority_len, normal_len, restricted_len = 0, 0, 0

        if priority_zones:
            priority_len: int = len(priority_zones)
            priority_zones.sort(key=lambda z: z.loc.x, reverse=True)

        if normal_zones:
            normal_len: int = len(normal_zones)
            normal_zones.sort(key=lambda z: z.loc.x, reverse=True)

        if restricted_zones:
            restricted_len: int = len(restricted_zones)
            restricted_zones.sort(key=lambda z: z.loc.x, reverse=True)

        def make_positional_weights(n: int, base: float = 1.2) -> list[float]:
            return [base ** (n - i - 1) for i in range(n)]

        final_zones: list[Zone] = (
            priority_zones + normal_zones + restricted_zones)
        weights = (
            [1] * priority_len + [0.5] * normal_len + [0.1] * restricted_len)
        weights = [w * p for w, p
                in zip(weights, make_positional_weights(len(final_zones)))]

        print("weights:", weights)

        return random.choices(final_zones, weights=weights)[0]
    """

    def move_to_zone(self, dest: Zone) -> None:

        if dest.zone == ZoneType.RESTRICTED:
            self.loc.update_occupancy(-1)
            self.last_zone = self.loc
            # self.loc = None
            self.buffer = dest
            self.buffer.update_occupancy(1)
            return

        self.last_zone = self.loc
        self.loc.update_occupancy(-1)
        self.loc = dest
        self.loc.update_occupancy(1)

    def clear_buff(self) -> bool:
        if self.buffer:
            # self.last_zone = self.loc
            # self.loc.update_occupancy(-1)
            self.loc = self.buffer
            # self.loc.update_occupancy(1)
            self.buffer = None
            return True
        return False

    def __str__(self) -> str:
        return f"Drone {self.index} at {self.loc}"
