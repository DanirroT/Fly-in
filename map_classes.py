from pydantic import (BaseModel, Field, field_validator,
                      ValidationError)  # model_validator
from typing import NamedTuple, Any
from enum import Enum
import sys

from validation_error_handling import error_processing


class DroneMap():
    nb_drones: int
    zones: list["Zone"]
    connections: list["Connection"]

    def __init__(self, nb_drones: int,
                 zones: list[tuple[str, str, "Coordinates", dict[str, str]]],
                 connections: list[tuple[str, str, dict[str, str]]]
                 ) -> None:

        self.nb_drones = nb_drones

        try:
            self.set_zones(zones)
        except ValueError as e:
            raise ValueError("An error has occurred while setting Zones\n"
                             f"Input: {zones}\nError: {e}")

        try:
            self.set_connections(connections)
        except ValueError as e:
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

        start: bool = False
        end: bool = False

        coords_present: list["Coordinates"] = []
        zone_names: set[str] = set()

        for zone in self.zones:
            if zone.hub_type is Hubs.START_HUB:
                if start:
                    raise ValueError(f"Multiple {Hubs.START_HUB} defined")
                start = True

            if zone.hub_type is Hubs.END_HUB:
                if end:
                    raise ValueError(f"Multiple {Hubs.END_HUB} defined")
                end = True

            if zone.loc in coords_present:
                raise ValueError("Multiple Zones with the same coordinates:",
                                 zone.loc)
            coords_present.append(zone.loc)

            if zone.name in zone_names:
                raise ValueError("Multiple Zones with the same name:",
                                 zone.loc)
            zone_names.update({zone.name})

    def set_zones(self,
                  zone_list: list[tuple[str, str, "Coordinates",
                                  dict[str, str]]]
                  ) -> None:
        self.zones = []
        for zone in zone_list:
            metadata = zone[-1]
            zone_dict = {k: v for k, v in
                         zip(["hub_type", "name", "loc"], zone[:-1])}
            for key in ["zone", "color", "max_drones"]:
                if key in metadata:
                    zone_dict[key] = metadata[key]
            try:
                self.zones.append(Zone(**zone_dict))
            except ValidationError as e:
                error_processing(e.errors())
                sys.exit()
            except ValueError:
                raise
        for zone in self.zones:
            zone.connections = []

    def set_connections(
            self,
            conn_list: list[tuple[str, str, "Coordinates", dict[str, str]]]
            ) -> None:
        self.connections = []
        for conn in conn_list:
            metadata = conn[-1]
            conn_dict = {k: v for k, v in
                         zip(["start", "end"], conn[:-1])}
            for key in ["max_link_capacity"]:
                if key in metadata:
                    conn_dict[key] = metadata[key]
            try:
                self.connections.append(Connection(**conn_dict))
            except ValidationError as e:
                error_processing(e.errors())
                sys.exit()
            except ValueError:
                raise

    def connect_zones(self) -> None:
        for connection in self.connections:
            for zone_i in self.zones:
                if connection.start == zone_i.name:
                    for zone_j in self.zones:
                        if connection.end == zone_j.name:
                            zone_i.connections.append(zone_j)
                            zone_j.connections.append(zone_i)

    def get_summary(self) -> dict[str, dict[str, dict[str, Any]]]:
        return {
            "Zones": {
                v.name: {"hub type": v.hub_type, "loc": v.loc,
                         "zone type": v.zone, "color": v.color,
                         "max_drones": v.max_drones, "connections": {
                            i: c
                            for i, c in enumerate(v.connections)
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

        return f"Zones:{sep1}{zones}\nConnections:{sep1}{conn}"


class Hubs(str, Enum):
    START_HUB = "start_hub"
    HUB = "hub"
    END_HUB = "end_hub"


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Coordinates(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}"


class Zone(BaseModel):
    name: str = Field(min_length=1)
    hub_type: str = Field(min_length=1)
    loc: Coordinates = Field()
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str = Field(min_length=1, default="none")
    max_drones: int = Field(gt=0, default=1)
    connections: list["Zone"] | None = Field(default=None)

    @field_validator("loc", mode="before")
    @classmethod
    def parse_coordinates(cls, v: str | Coordinates) -> Coordinates:
        """Parse coordinate strings like 'x,y' into coordinate tuples."""
        if isinstance(v, str):
            x, y = v.split(",")
            return Coordinates(int(x), int(y))
        return v

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
