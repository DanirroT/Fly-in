from map_classes import DroneMap, Zone, Connection, ZoneType, Hubs
import random

class Drone():
    last_zone: Zone
    loc: Zone
    buffer: Zone | None
    index: int

    def __init__(self, index: int) -> None:
        self.index = index

    def make_decision(self) -> Zone:
        normal_zones: list[Zone] = []
        priority_zones: list[Zone] = []
        restricted_zones: list[Zone] = []
        for zone in self.loc.get_connections():
            if zone.hub_type == Hubs.END_HUB:
                return zone
            if zone.zone == ZoneType.BLOCKED or zone == self.last_zone:
                continue
            elif zone.zone == ZoneType.NORMAL:
                normal_zones.append(zone)
            elif zone.zone == ZoneType.PRIORITY:
                priority_zones.append(zone)
            elif zone.zone == ZoneType.RESTRICTED:
                restricted_zones.append(zone)

        while priority_zones:
            list_len = len(priority_zones)
            if list_len == 1:
                if priority_zones[0] == self.last_zone:
                    break
                return priority_zones[0]
            priority_zones.sort(key=lambda z: z.loc.x)
            return (random.choices(
                priority_zones,
                [2 if i < list_len // 2 else 1
                 for i in range(list_len)]))

        return self.last_zone

    def move_to_zone(self, dest: Zone) -> None:

        if dest.zone == ZoneType.RESTRICTED:
            self.buffer = self.loc
            return

        self.last_zone = self.loc
        self.loc = dest

    def clear_buff(self) -> bool:
        if self.buffer:
            self.last_zone = self.loc
            self.loc = self.buffer
            self.buffer = None
            return True
        return False
