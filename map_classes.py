from pydantic import (BaseModel, Field, field_validator,
                      ValidationError, PrivateAttr)
from typing import NamedTuple, Any
from enum import Enum


class DroneMap():
    nb_drones: int
    zones: list["Zone"]
    start_zone: "Zone"
    end_zone: "Zone"
    connections: list["Connection"]
    grid: list[list["Zone"]]
    map_corners: tuple["Coordinates", "Coordinates"]

    def __init__(
            self, nb_drones: int,
            zones: list[tuple[str, str, "Coordinates", dict[str, str | int]]],
            connections: list[tuple[str, str, dict[str, int]]]
            ) -> None:

        self.nb_drones = nb_drones

        try:
            self.set_zones(zones)
        except ValueError as e:
            if isinstance(e, ValidationError):
                raise
            raise ValueError("An error has occurred while setting Zones\n"
                             f"Input: {zones}\nError: {e}")

        try:
            self.set_connections(connections)
        except ValueError as e:
            if isinstance(e, ValidationError):
                raise
            raise ValueError(
                "An error has occurred while setting Connections\n"
                f"Input: {connections}\nError: {e}")

        try:
            self.validate_inputs()
        except ValueError as e:
            raise ValueError("An error has occurred while Validating All Data"
                             f"\nError: {e}")

        self.connect_zones()

    def validate_inputs(self) -> None:

        start: Zone | None = None
        end: Zone | None = None

        coords_present: list["Coordinates"] = []
        zone_names: set[str] = set()

        for zone in self.zones:

            if zone.name in zone_names:
                raise ValueError(
                    f"Multiple Zones with the same name: {zone.loc}")
            zone_names.update({zone.name})

            if zone.hub_type == Hubs.START_HUB:
                if start:
                    raise ValueError(f"Multiple {Hubs.START_HUB} defined")
                start = zone
                zone.max_drones = self.nb_drones

            if zone.hub_type == Hubs.END_HUB:
                if end:
                    raise ValueError(f"Multiple {Hubs.END_HUB} defined")
                end = zone
                zone.max_drones = self.nb_drones

            if zone.loc in coords_present:
                raise ValueError(
                    f"Multiple Zones with the same coordinates: {zone.loc}")
            coords_present.append(zone.loc)

        if not start:
            raise ValueError(f"No {Hubs.START_HUB} defined")
        if not end:
            raise ValueError(f"No {Hubs.END_HUB} defined")

        self.start_zone = start
        self.end_zone = end

        max_x = max(c.x for c in coords_present)
        min_x = min(c.x for c in coords_present)
        max_y = max(c.y for c in coords_present)
        min_y = min(c.y for c in coords_present)
        self.map_corners = (Coordinates(min_x, min_y),
                            Coordinates(max_x, max_y))

    def set_zones(self,
                  zone_list: list[tuple[str, str, "Coordinates",
                                  dict[str, str | int]]]
                  ) -> None:
        self.zones = []
        for zone in zone_list:
            metadata = zone[-1]
            zone_dict: dict[str, str | Coordinates | int] = {
                k: v for k, v in zip(["hub_type", "name", "loc"], zone[:-1])}
            for key in ["zone", "color", "max_drones"]:
                if key in metadata:
                    zone_dict[key] = metadata[key]
            try:
                self.zones.append(Zone(**zone_dict))  # type: ignore
            except (ValidationError, ValueError):
                raise
        for zone in self.zones:
            zone.zero_connections()

    def set_connections(
            self,
            conn_list: list[tuple[str, str, dict[str, int]]]
            ) -> None:
        self.connections = []
        for conn in conn_list:
            metadata = conn[-1]
            conn_dict: dict[str, str | int] = {
                k: v for k, v in zip(["start", "end"], conn[:-1])}
            for key in ["max_link_capacity"]:
                if key in metadata:
                    conn_dict[key] = metadata[key]
            try:
                self.connections.append(
                    Connection(**conn_dict))  # type: ignore
            except (ValidationError, ValueError):
                raise

    def connect_zones(self) -> None:
        zone_lookup = {z.name: z for z in self.zones}

        for connection in self.connections:
            zone_i = zone_lookup.get(connection.start)
            zone_j = zone_lookup.get(connection.end)

            if not zone_i or not zone_j:
                raise ValueError("Invalid connection")

            zone_i.add_connection(zone_j)
            zone_j.add_connection(zone_i)

        # for connection in self.connections:
        #     for zone_i in self.zones:
        #         if connection.start == zone_i.name:
        #             for zone_j in self.zones:
        #                 if connection.end == zone_j.name:
        #                     zone_i.add_connection(zone_j)
        #                     zone_j.add_connection(zone_i)

        self.grid = [[  # type: ignore
            None for _ in range(self.map_corners[0].x,
                                self.map_corners[1].x + 1)
            ]
            for _ in range(self.map_corners[0].y,
                           self.map_corners[1].y + 1)]
        for zone in self.zones:
            y_ = zone.loc.y - self.map_corners[0].y
            x_ = zone.loc.x - self.map_corners[0].x
            self.grid[y_][x_] = zone

    def get_summary(self) -> dict[str, dict[str | int, dict[str, Any] | Any]]:
        return {
            "Zones": {
                v.name: {"hub type": v.hub_type, "loc": v.loc,
                         "zone type": v.zone, "color": v.color,
                         "max_drones": v.max_drones, "connections": {
                            i: c
                            for i, c in enumerate(v.get_connections())
                         }
                         }
                for v in self.zones
            },
            "Connections": {
                i: {"start": v.start, "end": v.end,
                    "max_link_capacity": v.max_link_capacity}
                for i, v in enumerate(self.connections)
            },
        }

    def get_nice_summary(self) -> str:
        summary = self.get_summary()
        sep1 = "\n\t"
        sep2 = "\n\t\t"
        sep3 = "\n\t\t\t"
        important_info = (
            f"Map Size  : {self.map_corners[1].x - self.map_corners[0].x + 1} "
            f"x {self.map_corners[1].y - self.map_corners[0].y + 1}\n"
            f"Start Zone: {self.start_zone.name} "
            f"at {self.start_zone.loc}\n"
            f"End Zone  : {self.end_zone.name} "
            f"at {self.end_zone.loc}\n\n"
        )
        zones = sep1.join([
            f"{name}: "
            f"{sep2.join(f'{i:10}:  {z}' for i, z in list(info.items())[:-1])}"
            f"{sep2}connections:{sep3}"
            f"""{sep3.join(f'{i}: {z.name}' for i, z
                           in list(info.values())[-1].items())}"""
            for name, info in summary['Zones'].items()
        ])
        conn = sep1.join([f"{index}: {sep2.join(map(str, info.items()))}"
                          for index, info in summary['Connections'].items()])

        return f"{important_info}Zones:{sep1}{zones}\nConnections:{sep1}{conn}"

    def print_map(self) -> None:
        print("Map Dimensions:",
              self.map_corners[1].x - self.map_corners[0].x + 1, "x",
              self.map_corners[1].y - self.map_corners[0].y + 1)
        tab = "    "
        print()
        for line in self.grid:
            print(tab.join([f"{zone.name if zone else '--------':8}"
                            for zone in line]))


class Hubs(str, Enum):
    START_HUB = "start_hub"
    HUB = "hub"
    END_HUB = "end_hub"

    def __str__(self) -> str:
        return self.value


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    def __str__(self) -> str:
        return self.value


class Coordinates(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}"


class Zone(BaseModel):
    name: str = Field(min_length=1)
    hub_type: Hubs = Field()
    loc: Coordinates = Field()
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str = Field(min_length=1, default="none")
    max_drones: int = Field(gt=0, default=1)
    _occupancy: int = PrivateAttr(default_factory=int)
    _zone_connections: list["Zone"] = PrivateAttr(default_factory=list["Zone"])

    @field_validator("loc", mode="before")
    @classmethod
    def parse_coordinates(cls, v: str | Coordinates) -> Coordinates:
        """Parse coordinate strings like 'x,y' into coordinate tuples."""
        if isinstance(v, str):
            x, y = v.split(",")
            return Coordinates(int(x), int(y))
        return v

    def zero_connections(self) -> None:
        self._zone_connections = []

    def get_connections(self) -> list["Zone"]:
        return list(self._zone_connections)

    def add_connection(self, add_zone: "Zone") -> None:
        if add_zone is self:
            raise ValueError(
                f"A Zone cannot be connected to itself: {self.name}")
        if add_zone not in self._zone_connections:
            self._zone_connections.append(add_zone)
        else:
            raise ValueError(f"Duplicate connection between "
                             f"{self.name} and {add_zone.name}")

    def zero_occupancy(self) -> None:
        self._occupancy = 0

    def get_occupancy(self) -> int:
        return self._occupancy

    def update_occupancy(self, delta: int) -> None:
        self._occupancy += delta
        if self._occupancy < 0:
            raise ValueError("Occupancy cannot be negative:", self.name)

    """
    @field_validator("metadata", mode="before")
    def parse_metadata(cls, v: list[str] | dict[str, str | int]
                       ) -> dict[str, str | int]:
        if isinstance(v, list):
            for cell in v:

                cell_split = cell.split(",")

                if len(cell_split) != 2:
                    raise ValueError(
                        f"{cell} "
                        "is not formatted correctly.\n"
                        "\tCorrect formatting is: <data>=<value>"
                    )

                if cell_split[0] not in ["zone", "color", "max_drones"]:

                try:
                    x = int(cell_split[0])
                    y = int(cell_split[1])
                except ValueError as e:
                    raise ValueError(
                        "cell's 2 values must be Integers. "
                        f"{cell}\nValueError: {e}"
                    )

            return {"zone": zone if zone else "normal",
                    "color": color if color else "none",
                    "max_drones": max_drones if max_drones else 1,
                    }

        return v
        """


class Connection(BaseModel):
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)
    max_link_capacity: int = Field(gt=0, default=1)
