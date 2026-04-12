from pydantic import (BaseModel, Field, model_validator,
                      field_validator, ValidationError)
from typing import NamedTuple
from enum import Enum
import sys

from validation_error_handling import error_processing


class DroneMap():
    nb_drones: int
    zones: list["Zone"]
    connections: list["Connection"]

    def __init__(self, nb_drones: int,
                 zones: list[tuple[str, str, "Coordinates", list[str]]],
                 connections: list[tuple[str, str, list[str]]]
                 ) -> None:

        self.nb_drones = nb_drones

        try:
            self.set_zones(zones)
        except ValueError as e:
            raise ValueError("An error has occured while setting Zones\n"
                             f"Input: {zones}\nError: {e}")

        try:
            self.set_connections(connections)
        except ValueError as e:
            raise ValueError("An error has occured while setting Connections\n"
                             f"Input: {connections}\nError: {e}")

        try:
            self.validate_inputs()
        except ValueError as e:
            raise ValueError("An error has occured while Validating All Data\n"
                             f"nError: {e}")

    def validate_inputs(self) -> None:

        start: bool = False
        end: bool = False

        coords_present: list["Coordinates"] = []
        zone_names: set[str] = set()
        for zone in self.zones:
            if zone.hub_type in Hubs.START_HUB:
                if start:
                    raise ValueError(f"Multiple {Hubs.START_HUB} defined")
                start = True

            if zone.hub_type in Hubs.END_HUB:
                if end:
                    raise ValueError(f"Multiple {Hubs.END_HUB} defined")
                end = True

            if zone.loc in coords_present:
                raise ValueError("Multiple Zones with the same coordenates:",
                                 zone.loc)
            coords_present.append(zone.loc)

            if zone.name in zone_names:
                raise ValueError("Multiple Zones with the same name:",
                                 zone.loc)
            zone_names.update(zone.name)

        print(zone_names)

    def set_zones(self,
                  zone_list: list[tuple[str, str, "Coordinates", list[str]]]
                  ) -> None:
        self.zones = []
        for zone in zone_list:
            try:
                self.zones.append(Zone(**{k: v for k, v in
                                  zip(["hub_type", "name", "loc",
                                       "zone", "color", "max_drones"],
                                      zone)}))
            except ValidationError as e:
                error_processing(e.errors())
                sys.exit()
            except ValueError:
                raise

    def set_connections(
            self,
            conn_list: list[tuple[str, str, "Coordinates", list[str]]]
            ) -> None:
        self.connections = []
        for connections in conn_list:
            try:
                self.connections.append(Connection(**{k: v for k, v in
                                        zip(["start", "end",
                                             "max_link_capacity"],
                                            connections)}))
            except ValidationError as e:
                error_processing(e.errors())
                sys.exit()
            except ValueError:
                raise


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
    connections: list["Zone"]

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
                        "\tCorrect formatig is: <data>=<value>"
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
    max_link_capacity: int = Field()
