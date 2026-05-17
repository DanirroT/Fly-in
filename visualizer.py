# from abc import ABC, abstractmethod

from map_classes import Zone, Hubs, ZoneType
from map_classes import Coordinates, DroneMap, Colors
from enum import Enum
from typing import NamedTuple, Literal
from math import cos, sin, pi

import pygame
from pygame import Rect, Surface
# from pygame.locals import Rect, Font
import random


class CoordinatesFloat(NamedTuple):
    x: float
    y: float

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}"


def terminal_clear() -> None:
    print("\033[H\033[J", end="")


"""
class Visualizer(ABC):

    drone_map: DroneMap

    def __init__(self, drone_map: DroneMap) -> None:
        self.drone_map = drone_map

    @abstractmethod
    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pass

    @abstractmethod
    def terminate(self) -> None:
        pass
"""


class ColorsVals(tuple[int, int, int], Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    DARKRED = (127, 0, 0)
    DARKGREEN = (0, 127, 0)
    DARKBLUE = (0, 0, 127)

    BLACK = (0, 0, 0)
    DARKGREY = (63, 63, 63)
    GREY = (127, 127, 127)
    LIGHTGREY = (190, 190, 190)
    WHITE = (255, 255, 255)
    BROWN = (136, 97, 39)

    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

    ORANGE = (255, 127, 0)
    PURPLE = (127, 0, 255)
    LIME = (200, 225, 100)
    LIGHTBLUE = (100, 225, 225)

    GOLD = (255, 207, 64)
    MAROON = (80, 0, 0)
    CRIMSON = (120, 6, 6)
    PINK = (255, 167, 225)
    VIOLET = (180, 0, 255)

    NONE = (150, 150, 150)

    def __str__(self) -> str:
        return str(self.value)


class WindowedVisualizer():

    screen: Surface
    background: Surface
    dimensions: Coordinates = Coordinates(1200, 700)
    margins: Coordinates = Coordinates(100, 75)
    text_margin: int = 20
    text_size: int = 30
    menu_hight: int = 100
    stars: list[Coordinates]
    drone_pos: list[Rect]
    # font: Font
    scale: Coordinates
    middle_map: CoordinatesFloat
    drone_png: Surface

    def __init__(self, map: DroneMap) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(self.dimensions)
        self.drone_map = map

        pygame.font.init()
        pygame.display.set_caption("Fly-in")
        self.font = pygame.font.SysFont('freesanbold.ttf', self.text_size)
        self.stars = []
        for _ in range(50):
            self.stars.append(Coordinates(
                random.choice(range(120)),
                random.choice(range(100)))
            )
        self.build_map()

        # print(self.drone_map.nb_drones)

        if self.drone_map.nb_drones >= 25:
            drone_size = (20, 20)
        elif self.drone_map.nb_drones >= 10:
            drone_size = (30, 30)

        elif self.drone_map.nb_drones >= 5:
            drone_size = (40, 40)

        else:
            drone_size = (50, 50)

        self.drone_png = pygame.image.load('drone.png')
        self.drone_png = pygame.transform.scale(self.drone_png, drone_size)
        self.drone_png.convert_alpha()
        drone_rect = self.drone_png.get_rect()
        drone_rect.center = self.pos_to_display(self.drone_map.start_zone.loc)
        # for _ in self.drone_map.nb_drones:
        self.drone_pos = [
            drone_rect.copy()
            for _ in range(self.drone_map.nb_drones)
        ]
        # self.update_display([self.drone_map.start_zone])

        pygame.display.update()

    def pos_to_display(self, pos: Coordinates | CoordinatesFloat
                       ) -> Coordinates:
        # print()
        # print()
        # print(pos)
        # print()
        # print(Coordinates(
        #     round(((pos.x - middle.x) * scale.x) + self.dimensions.x/2),
        #     round(((pos.y - middle.y) * -scale.y)
        #           + (self.dimensions.y/2) - (self.menu_hight/2))))

        return Coordinates(
            round(
                ((pos.x - self.middle_map.x) * self.scale.x)
                + self.dimensions.x/2),
            round(
                ((pos.y - self.middle_map.y) * -self.scale.y) -
                self.text_margin + (self.dimensions.y/2) - (self.menu_hight/2))
        )

    @staticmethod
    def mod_color(color: tuple[int, int, int],
                  factor: float
                  ) -> tuple[int, int, int]:

                return tuple(
                    min(255, max(0, int(c * factor)))
                    for c in color
                )

    # @staticmethod
    # def mod_color(color: tuple[int, int, int],
    #               mod: Literal["darker"] | Literal["lighter"]
    #               ) -> tuple[int, int, int]:

    #     if mod == "darker":
    #         return tuple(
    #             max(0, min(255, int(c * 0.7)))
    #             for c in color
    #         )

    #     elif mod == "lighter":
    #         return tuple(
    #             min(255, max(0, int(c + (255 - c) * 0.7)))
    #             for c in color
    #         )

    #     else:
    #         raise ValueError(f"Mod Value not valid: {mod}")

    def build_map(self) -> None:
        self.screen = pygame.display.set_mode(self.dimensions,
                                              pygame.RESIZABLE)
        self.background = pygame.Surface(self.dimensions)

        self.background.fill((3, 20, 56))

        bottom_right, top_left = self.drone_map.map_corners
        delta_x = top_left.x - bottom_right.x
        delta_y = top_left.y - bottom_right.y
        # _y = float(delta_y/2 % 1)
        self.middle_map = (
            CoordinatesFloat(delta_x/2, delta_y/2 + bottom_right.y))

        self.scale = Coordinates(
            round((self.dimensions.x - (2 * self.margins.x)) / (delta_x + 1)),
            round((self.dimensions.y - (2 * self.margins.y) + self.menu_hight)
                  / (delta_y + 1))
        )

        """
        print("Map delta_x:", top_left.x, bottom_right.x, delta_x, sep=" | ")
        print("Map delta_y:", bottom_right.y, top_left.y, delta_y, sep=" | ")
        print("Map Corners:", bottom_right, top_left)

        middle_display = Coordinates(round(self.dimensions.x/2),
                                     round(self.dimensions.y/2
                                           - self.menu_hight/2))

        print()
        print("scale:", self.scale)
        print()
        print("middle-display:", middle_display)
        print()
        print("middle-map:", self.middle_map)
        print()
        print("middle-convert:", self.pos_to_display(self.middle_map))
        print()
        pygame.draw.line(self.screen, (0, 0, 0),
                         self.dimensions, (0, 0), 5)
        pygame.draw.line(self.screen, (0, 0, 0),
                         (0, self.dimensions.y), (self.dimensions.x, 0), 5)

        pygame.draw.line(self.screen, (0, 0, 0),
                         (self.dimensions.x, middle_display.y),
                         (0, middle_display.y), 5)
        pygame.draw.line(self.screen, (0, 0, 0),
                         (middle_display.x, self.dimensions.y),
                         (middle_display.x, 0), 5)
        """

        for star in self.stars:
            star_loc = Coordinates(round((star.x * self.dimensions.x) / 120),
                                   round((star.y * self.dimensions.y) / 100))
            pygame.draw.circle(self.background, (255, 255, 255),
                               star_loc, 2, 0)

        self.draw_connection()
        self.draw_zones()
        self.draw_menu()

    def draw_connection(self) -> None:

        for connection in self.drone_map.connections:

            start_coords: None | Coordinates = None
            end_coords: None | Coordinates = None

            for zone in self.drone_map.zones:
                if zone.name == connection.start:
                    start_coords = self.pos_to_display(zone.loc)
                    # print(zone.loc, end=", ")
                    # print([start_coords, end_coords])
                if zone.name == connection.end:
                    end_coords = self.pos_to_display(zone.loc)
                    # print(zone.loc, end=", ")
                    # print([start_coords, end_coords])
                if start_coords and end_coords:
                    break

            # print(" -> ", [start_coords, end_coords])
            if not start_coords or not end_coords:
                raise TypeError("Somehow while drawing, there was an error")
            pygame.draw.line(
                self.background, (0, 0, 0), start_coords, end_coords, 5)

    def draw_zones(self) -> None:
        for zone in self.drone_map.zones:
            # print(zone.loc, end=" -> ")
            coords_list = self.pos_to_display(zone.loc)
            # print(coords_list)
            display_name = zone.name.replace("_", " ")
            text1 = self.font.render(display_name, True, (5, 5, 5))
            color_vals = ColorsVals.__dict__
            str_exclusion = str.__dict__
            enum_exclusion = Enum.__dict__
            if zone.color == Colors.RAINBOW:
                top_right = [coords_list.x - 15, coords_list.y + 15]
                top_center = [coords_list.x, coords_list.y + 15]
                top_left = [coords_list.x + 15, coords_list.y + 15]
                bottom_right = [coords_list.x - 15, coords_list.y - 15]
                bottom_center = [coords_list.x, coords_list.y - 15]
                bottom_left = [coords_list.x + 15, coords_list.y - 15]

                pygame.draw.polygon(
                    self.background, (255, 0, 0),
                    [top_right, top_center, bottom_right])
                pygame.draw.polygon(
                    self.background, (0, 255, 0),
                    [top_center, top_left, bottom_center, bottom_right])
                pygame.draw.polygon(
                    self.background, (0, 0, 255),
                    [top_left, bottom_center, bottom_left])

                grey = (128, 128, 128)

                if zone.zone is ZoneType.BLOCKED:
                    pygame.draw.line(
                        self.background, self.mod_color(grey, 0.7),
                        ((coords_list.x + 20), (coords_list.y + 20)),
                        ((coords_list.x - 20), (coords_list.y - 20)), 8)
                    pygame.draw.line(
                        self.background, self.mod_color(grey, 0.7),
                        ((coords_list.x + 20), (coords_list.y - 20)),
                        ((coords_list.x - 20), (coords_list.y + 20)), 8)

                if zone.zone is ZoneType.RESTRICTED:
                    pygame.draw.line(
                        self.background, self.mod_color(grey, 0.7),
                        ((coords_list.x + 5), (coords_list.y + 5)),
                        ((coords_list.x - 5), (coords_list.y - 5)), 5)
                    pygame.draw.line(
                        self.background, self.mod_color(grey, 0.7),
                        ((coords_list.x + 5), (coords_list.y - 5)),
                        ((coords_list.x - 5), (coords_list.y + 5)), 5)

                if zone.zone is ZoneType.PRIORITY:

                    pygame.draw.polygon(
                        self.background, self.mod_color(grey, 1.7),
                        [((coords_list.x), (coords_list.y - 10)),

                         (round(coords_list.x - (sin((1/5) * pi) * 4)),
                          round(coords_list.y - (cos((1/5) * pi) * 4))),

                         (round(coords_list.x - (sin((2/5) * pi) * 10)),
                          round(coords_list.y - (cos((2/5) * pi) * 10))),

                         (round(coords_list.x - (sin((3/5) * pi) * 4)),
                          round(coords_list.y - (cos((3/5) * pi) * 4))),

                         (round(coords_list.x - (sin((4/5) * pi) * 10)),
                          round(coords_list.y - (cos((4/5) * pi) * 10))),

                         (coords_list.x, round(coords_list.y + 4)),

                         (round(coords_list.x + (sin((4/5) * pi) * 10)),
                          round(coords_list.y - (cos((4/5) * pi) * 10))),

                         (round(coords_list.x + (sin((3/5) * pi) * 4)),
                          round(coords_list.y - (cos((3/5) * pi) * 4))),

                         (round(coords_list.x + (sin((2/5) * pi) * 10)),
                          round(coords_list.y - (cos((2/5) * pi) * 10))),

                         (round(coords_list.x + (sin((1/5) * pi) * 4)),
                          round(coords_list.y - (cos((1/5) * pi) * 4))),
                         ])

                if zone.hub_type is Hubs.START_HUB:
                    pygame.draw.polygon(
                        self.background, self.mod_color(grey, 1.7),
                        [(round(coords_list.x - (cos((2/3) * pi) + 5)),
                          round(coords_list.y - (sin((2/3) * pi) + 5))),
                         (round(coords_list.x - (cos((2/3) * pi) + 5)),
                          round(coords_list.y + (sin((2/3) * pi) + 5))),
                         ((coords_list.x + 5), (coords_list.y))])

                if zone.hub_type is Hubs.END_HUB:
                    pygame.draw.polygon(
                        self.background, self.mod_color(grey, 0.7),
                        [((coords_list.x + 4), (coords_list.y + 4)),
                         ((coords_list.x + 4), (coords_list.y - 4)),
                         ((coords_list.x - 4), (coords_list.y - 4)),
                         ((coords_list.x - 4), (coords_list.y + 4))])

                text1 = self.font.render(display_name, True, ColorsVals.PINK)
            else:
                color_val = (150, 150, 150)
                for vals_key in color_vals.keys():
                    if (zone.color == vals_key.lower() and vals_key not in
                            str_exclusion and vals_key not in enum_exclusion):
                        color_val = color_vals[vals_key]
                        break
                text1 = self.font.render(display_name, True, color_val)
                pygame.draw.circle(self.background, color_val,
                                   coords_list, 15, 0)

                if zone.zone is ZoneType.BLOCKED:
                    pygame.draw.line(
                        self.background, self.mod_color(color_val, 0.7),
                        ((coords_list.x + 20), (coords_list.y + 20)),
                        ((coords_list.x - 20), (coords_list.y - 20)), 8)
                    pygame.draw.line(
                        self.background, self.mod_color(color_val, 0.7),
                        ((coords_list.x + 20), (coords_list.y - 20)),
                        ((coords_list.x - 20), (coords_list.y + 20)), 8)

                if zone.zone is ZoneType.RESTRICTED:
                    pygame.draw.line(
                        self.background, self.mod_color(color_val, 0.7),
                        ((coords_list.x + 5), (coords_list.y + 5)),
                        ((coords_list.x - 5), (coords_list.y - 5)), 5)
                    pygame.draw.line(
                        self.background, self.mod_color(color_val, 0.7),
                        ((coords_list.x + 5), (coords_list.y - 5)),
                        ((coords_list.x - 5), (coords_list.y + 5)), 5)

                if zone.zone is ZoneType.PRIORITY:

                    pygame.draw.polygon(
                        self.background, self.mod_color(color_val, 1.7),
                        [((coords_list.x), (coords_list.y - 10)),

                         (round(coords_list.x - (sin((1/5) * pi) * 4)),
                          round(coords_list.y - (cos((1/5) * pi) * 4))),

                         (round(coords_list.x - (sin((2/5) * pi) * 10)),
                          round(coords_list.y - (cos((2/5) * pi) * 10))),

                         (round(coords_list.x - (sin((3/5) * pi) * 4)),
                          round(coords_list.y - (cos((3/5) * pi) * 4))),

                         (round(coords_list.x - (sin((4/5) * pi) * 10)),
                          round(coords_list.y - (cos((4/5) * pi) * 10))),

                         (coords_list.x, round(coords_list.y + 4)),

                         (round(coords_list.x + (sin((4/5) * pi) * 10)),
                          round(coords_list.y - (cos((4/5) * pi) * 10))),

                         (round(coords_list.x + (sin((3/5) * pi) * 4)),
                          round(coords_list.y - (cos((3/5) * pi) * 4))),

                         (round(coords_list.x + (sin((2/5) * pi) * 10)),
                          round(coords_list.y - (cos((2/5) * pi) * 10))),

                         (round(coords_list.x + (sin((1/5) * pi) * 4)),
                          round(coords_list.y - (cos((1/5) * pi) * 4))),
                         ])

                    """
                    # pygame.draw.polygon(
                    #     self.background, self.mod_color(color_val, 0.7),
                    #     [((coords_list.x), (coords_list.y - 5)),

                    #      (round(coords_list.x - (sin((2/5) * pi) * 5)),
                    #       round(coords_list.y - (cos((2/5) * pi) * 5))),

                    #      (round(coords_list.x - (sin((4/5) * pi) * 5)),
                    #       round(coords_list.y - (cos((4/5) * pi) * 5))),

                    #      (round(coords_list.x + (sin((4/5) * pi) * 5)),
                    #       round(coords_list.y - (cos((4/5) * pi) * 5))),

                    #      (round(coords_list.x + (sin((2/5) * pi) * 5)),
                    #       round(coords_list.y - (cos((2/5) * pi) * 5))),
                    #      ])

                    pygame.draw.circle(
                        self.background, (0, 0, 0),
                        ((coords_list.x), (coords_list.y - 5)),
                        5, 0)

                    pygame.draw.circle(
                        self.background, (0, 0, 0),
                        (round(coords_list.x - (sin((2/5) * pi) * 5)),
                         round(coords_list.y - (cos((2/5) * pi) * 5))),
                        5, 0)

                    pygame.draw.circle(
                        self.background, (255, 255, 255),
                        (round(coords_list.x + (sin((2/5) * pi) * 5)),
                         round(coords_list.y - (cos((2/5) * pi) * 5))),
                        5, 0)

                    pygame.draw.circle(
                        self.background, (0, 0, 0),
                        (round(coords_list.x - (sin((4/5) * pi) * 5)),
                         round(coords_list.y - (cos((4/5) * pi) * 5))),
                        5, 0)

                    pygame.draw.circle(
                        self.background, (255, 255, 255),
                        (round(coords_list.x + (sin((4/5) * pi) * 5)),
                         round(coords_list.y - (cos((4/5) * pi) * 5))),
                        5, 0)
                    """

                if zone.hub_type is Hubs.START_HUB:
                    pygame.draw.polygon(
                        self.background, self.mod_color(color_val, 1.7),
                        [(round(coords_list.x - (cos((2/3) * pi) + 5)),
                          round(coords_list.y - (sin((2/3) * pi) + 5))),
                         (round(coords_list.x - (cos((2/3) * pi) + 5)),
                          round(coords_list.y + (sin((2/3) * pi) + 5))),
                         ((coords_list.x + 5), (coords_list.y))])

                if zone.hub_type is Hubs.END_HUB:
                    pygame.draw.polygon(
                        self.background, self.mod_color(color_val, 0.7),
                        [((coords_list.x + 4), (coords_list.y + 4)),
                         ((coords_list.x + 4), (coords_list.y - 4)),
                         ((coords_list.x - 4), (coords_list.y - 4)),
                         ((coords_list.x - 4), (coords_list.y + 4))])

            text_offset = round(coords_list.y + (self.text_size) +
                                ((zone.loc.x % 2) * (self.text_size * 0.75)))
            text_rect = text1.get_rect()
            text_rect.center = (coords_list.x, text_offset)
            self.background.blit(text1, text_rect)

    def draw_menu(self) -> None:

        pygame.draw.rect(
            self.background, (150, 150, 150),
            (0, self.dimensions.y-self.menu_hight,
             self.dimensions.x, self.menu_hight)
        )
        menu_space_center = (round(self.dimensions.x/2),
                             round(self.dimensions.y - self.menu_hight/2))
        menu_str_1 = "Use arrows <- / -> to cycle Turns"
        menu_text = self.font.render(menu_str_1, True, (0, 0, 0))
        menu_text_rect = menu_text.get_rect()
        menu_space_center_offset = (menu_space_center[0],
                                    menu_space_center[1] - self.text_margin)
        menu_text_rect.center = menu_space_center_offset
        self.background.blit(menu_text, menu_text_rect)

        menu_str_2 = "Use Q or Esc to Quit"
        menu_text = self.font.render(menu_str_2, True, (0, 0, 0))
        menu_text_rect = menu_text.get_rect()
        menu_space_center_offset = (menu_space_center[0],
                                    menu_space_center[1] + self.text_margin)
        menu_text_rect.center = menu_space_center_offset
        self.background.blit(menu_text, menu_text_rect)

    def resize(self, w: int, h: int, turn: int,
               drone_locs: list[Zone]) -> None:
        self.dimensions = Coordinates(w, h)

        # print("resize to:", w, h)
        self.build_map()
        self.update_display(turn, drone_locs)
        pygame.display.update()

    def update_display(self, turn: int, drone_locs: list[Zone]) -> None:

        # print()
        # print("\n".join(map(str, drone_locs)))
        # print()
        # print()
        # print("\n".join(map(str, self.drone_pos)))

        zone_checker = drone_locs.copy()

        self.screen.blit(self.background, (0, 0))

        for i, drone_loc in enumerate(drone_locs):
            _x, _y = self.pos_to_display(drone_loc.loc)

            # cap_div4 = zone_checker.count(drone_loc) % 4

            zone_checker.pop(zone_checker.index(drone_loc))

            offset = 20

            angle = ((2 * pi * zone_checker.count(drone_loc))
                     / drone_locs.count(drone_loc))
            x_offset = round(cos(angle - pi/2) * offset)
            y_offset = round(sin(angle - pi/2) * offset)

            # x_offset = -offset if (cap_div4 in (1, 3)) else offset
            # y_offset = -offset if (cap_div4 in (1, 2)) else offset

            self.drone_pos[i].center = (_x + x_offset, _y + y_offset)
            self.screen.blit(self.drone_png, self.drone_pos[i])
            # print("drone put in", drone_loc.loc)

        # print()
        # print("\n".join(map(str, self.drone_pos)))

        # print()
        # print("\n".join(map(str, drone_locs)))

        # print(turn)

        turn_text = self.font.render(f"Turn: {turn}", True, (0, 0, 0))
        turn_rect = turn_text.get_rect()
        turn_rect.center = (50, round(self.dimensions.y - self.menu_hight / 2))
        turn_rect.left = 20
        # print(turn_rect.center)
        self.screen.blit(turn_text, turn_rect)

        pygame.display.update()

    def terminate(self) -> None:
        pygame.quit()


"""
class TerminalVisualizer(Visualizer):

    def __init__(self, map: DroneMap) -> None:
        super().__init__(map)
        terminal_clear()

    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pass

    def terminate(self) -> None:
        pass
"""

"""
from input import read_map_file

if __name__ == "__main__":

    # file_name = "maps/easy/01_linear_path.txt"
    file_name = "maps/hard/01_maze_nightmare.txt"
    # file_name = "maps/challenger/01_the_impossible_dream.txt"

    drone_map = read_map_file(file_name)

    visualizer = WindowedVisualizer(drone_map)

    run = True

    while run:

        # Iterating over all the events received from
        # pygame.event.get()
        for event in pygame.event.get():

            # If the type of the event is quit
            # then setting the run variable to false
            if event.type == pygame.QUIT:
                print("Quit")
                run = False

    visualizer.terminate()
"""
