from map_classes import DroneMap, Zone, ZoneType, Hubs
import random


class DroneManager():
    drones: list["Drone"]
    drone_map: DroneMap
    usable_zones: list[Zone]

    def __init__(self, drone_map: DroneMap, nb_drones: int) -> None:
        self.drone_map = drone_map
        self.drones = [Drone(i, self.drone_map.start_zone)
                       for i in range(nb_drones)]
        self.usable_zones = [zone for zone in self.drone_map.zones
                             if zone.zone != ZoneType.BLOCKED
                             and zone.hub_type != Hubs.START_HUB]

    def sim_turn(self, nb_drones: int) -> None:
        dests: list[Zone] = [None for _ in range(nb_drones)]

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
            empty_spots[dest] = dest.capacity - dest.get_occupancy()
        for _ in range(2):
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
                        full.update(dest_list)


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

    def make_decision(self, usable_zones: list[Zone] | None = None) -> Zone:
        normal_zones: list[Zone] = []
        priority_zones: list[Zone] = []
        restricted_zones: list[Zone] = []
        zone_connections: list[Zone] = self.loc.get_connections()
        if usable_zones is None:
            usable_zones = [zone for zone in zone_connections
                            if (zone.zone != ZoneType.BLOCKED
                                and zone.hub_type != Hubs.START_HUB)]
        if len(zone_connections) == 1:
            return zone_connections[0]
        back_index: int = zone_connections.index(self.last_zone)
        if len(zone_connections) == 2:
            return zone_connections[1 - back_index]
        for zone in zone_connections:
            if zone.hub_type == Hubs.END_HUB:
                return zone
            if zone not in usable_zones:
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

    def move_to_zone(self, dest: Zone) -> None:

        if dest.zone == ZoneType.RESTRICTED:
            self.buffer = dest
            return

        self.last_zone = self.loc
        self.loc.add_occupancy(-1)
        self.loc = dest
        self.loc.add_occupancy(1)

    def clear_buff(self) -> bool:
        if self.buffer:
            self.last_zone = self.loc
            self.loc.add_occupancy(-1)
            self.loc = self.buffer
            self.loc.add_occupancy(1)
            self.buffer = None
            return True
        return False
