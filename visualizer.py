# from abc import ABC, abstractmethod

from map_classes import Zone
from map_classes import Coordinates, DroneMap, Colors
from enum import Enum


import pygame
import random


def terminal_clear() -> None:
    print("\033[H\033[J", end="")


# class Visualizer(ABC):

#     drone_map: DroneMap

#     def __init__(self, drone_map: DroneMap) -> None:
#         self.drone_map = drone_map

#     @abstractmethod
#     def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
#         pass

#     @abstractmethod
#     def terminate(self) -> None:
#         pass


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
    LIME = (255, 100, 100)
    # LIGHTBLUE = (255, 0, 0)

    GOLD = (255, 207, 64)
    MAROON = (80, 0, 0)
    CRIMSON = (120, 6, 6)
    PINK = (255, 153, 153)
    VIOLET = (180, 0, 255)

    NONE = (150, 150, 150)

    def __str__(self) -> str:
        return str(self.value)


class WindowedVisualizer():

    # screen: Surface
    dimensions: Coordinates
    margins: Coordinates = Coordinates(100, 50)
    menu_hight: int
    # working_dimensions: Coordinates
    stars: list[Coordinates]
    # font: Font

    def __init__(self, map: DroneMap) -> None:
        self.drone_map = map
        self.menu_hight = 100
        self.dimensions = Coordinates(1200, 700)
        # self.working_dimensions = Coordinates(self.dimensions.x - 100,
        #                                       self.dimensions.y - 100)

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Fly-in")
        self.font = pygame.font.SysFont('freesanbold.ttf', 30)
        self.stars = []
        for _ in range(50):
            self.stars.append(Coordinates(
                random.choice(range(120)),
                random.choice(range(100)))
            )
        self.build_map()
        pygame.display.update()

    def pos_to_display(self, pos: Coordinates, middle: Coordinates,
                       scale: Coordinates) -> Coordinates:

        return Coordinates(
            round(((pos.x - middle.x) * scale.x) + self.dimensions.x/2),
            round(((pos.y - middle.y) * scale.y - (self.menu_hight/2))
                  + self.dimensions.y/2)
        )

    def build_map(self) -> None:
        self.screen = pygame.display.set_mode(self.dimensions,
                                              pygame.RESIZABLE)
        self.screen.fill((3, 20, 56))

        bottom_right, top_left = self.drone_map.map_corners
        delta_x = top_left.x - bottom_right.x + 1
        delta_y = top_left.y - bottom_right.y + 1
        # print("Map delta_x:", top_left.x, bottom_right.x, delta_x, sep=" | ")
        # print("Map delta_y:", bottom_right.y, top_left.y, delta_y, sep=" | ")
        # print("Map Corners:", bottom_right, top_left)
        _y = float(delta_y/2 % 1)
        middle_map = Coordinates(round(delta_x/2), round(_y))
        # middle_display = Coordinates(round(self.dimensions.x/2),
        #                              round(self.dimensions.y/2))
        # print(middle_map)

        scale_x = (self.dimensions.x - 2 * self.margins.x) / delta_x
        scale_y = ((self.dimensions.y - 2 * (self.margins.y + self.menu_hight))
                   / delta_y)

        scale = Coordinates(round(scale_x), round(scale_y))
        # print(scale)

        for star in self.stars:
            star_loc = Coordinates(round((star.x * self.dimensions.x) / 120),
                                   round((star.y * self.dimensions.y) / 100))
            pygame.draw.circle(self.screen, (255, 255, 255),
                               star_loc, 2, 0)

        for connection in self.drone_map.connections:

            start_coords: None | Coordinates = None
            end_coords: None | Coordinates = None

            for zone in self.drone_map.zones:
                if zone.name == connection.start:
                    start_coords = self.pos_to_display(
                        zone.loc, middle_map, scale)
                    # print(zone.loc, end=", ")
                    # print([start_coords, end_coords])
                if zone.name == connection.end:
                    end_coords = self.pos_to_display(
                        zone.loc, middle_map, scale)
                    # print(zone.loc, end=", ")
                    # print([start_coords, end_coords])
                if start_coords and end_coords:
                    break

            # print(" -> ", [start_coords, end_coords])
            if not start_coords or not end_coords:
                raise TypeError("Somehow while drawing, there was an error")
            pygame.draw.line(
                self.screen, (0, 0, 0), start_coords, end_coords, 5)

        # print()
        # print(middle_map)

        # print()
        # print(middle_map_display)
        # print()
        # print(middle_display)
        # print()
        # pygame.draw.line(self.screen, (0, 0, 0),
        #                  self.dimensions, (0, 0), 5)
        # pygame.draw.line(self.screen, (0, 0, 0),
        #                  (0, self.dimensions.y), (self.dimensions.x, 0), 5)

        # pygame.draw.line(self.screen, (0, 0, 0),
        #                  (self.dimensions.x, middle_display.y),
        #                  (0, middle_display.y), 5)
        # pygame.draw.line(self.screen, (0, 0, 0),
        #                  (middle_display.x, self.dimensions.y),
        #                  (middle_display.x, 0), 5)

        # pygame.draw.line(self.screen, (0, 0, 0),
        #                  (self.dimensions.x, middle_map_display.y),
        #                  (0, middle_map_display.y), 5)
        # pygame.draw.line(self.screen, (0, 0, 0),
        #                  (middle_map_display.x, self.dimensions.y),
        #                  (middle_map_display.x, 0), 5)

        for zone in self.drone_map.zones:
            # print(zone.loc, end=" -> ")
            coords_list = self.pos_to_display(zone.loc, middle_map, scale)
            # print(coords_list)
            text1 = self.font.render(zone.name, True, (5, 5, 5))
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
                    self.screen, (255, 0, 0),
                    [top_right, top_center, bottom_right])
                pygame.draw.polygon(
                    self.screen, (0, 255, 0),
                    [top_center, top_left, bottom_center, bottom_right])
                pygame.draw.polygon(
                    self.screen, (0, 0, 255),
                    [top_left, bottom_center, bottom_left])
                text1 = self.font.render(zone.name, True, ColorsVals.PINK)
            else:
                color_val = (150, 150, 150)
                for vals_key in color_vals.keys():
                    if (zone.color == vals_key.lower() and vals_key not in
                            str_exclusion and vals_key not in enum_exclusion):
                        color_val = color_vals[vals_key]
                        break
                text1 = self.font.render(zone.name, True, color_val)
                pygame.draw.circle(self.screen, color_val,
                                   coords_list, 15, 0)
            text_offset = coords_list.y + 40 + ((zone.loc.x % 2) * 25)
            text_rect = text1.get_rect()
            text_rect.center = (coords_list.x, text_offset)
            self.screen.blit(text1, text_rect)

        menu_space = pygame.draw.rect(
            self.screen, (150, 150, 150),
            (0, self.dimensions.y-self.menu_hight,
             self.dimensions.x, self.menu_hight)
        )
        menu_str = (
            "Use arrows <- / -> to cycle Turns\n"
            "Use Q or Esc to Quit"
        )
        menu_text = self.font.render(menu_str, True, (0, 0, 0))
        self.screen.blit(menu_text, menu_space, menu_space)

    def resize(self, w: int, h: int) -> None:
        self.dimensions = Coordinates(w, h)

        # print("resize to:", w, h)

        # self.working_dimensions = Coordinates(
        #     self.dimensions.x - 100,
        #     self.dimensions.y - 100
        # )
        self.build_map()
        pygame.display.update()
        # self.redraw()

    def update_display(self, drone_locs: list[Zone]) -> None:
        print("\n".join(map(str, drone_locs)))
        pygame.display.update()

    def terminate(self) -> None:
        pygame.quit()


# class TerminalVisualizer(Visualizer):

#     def __init__(self, map: DroneMap) -> None:
#         super().__init__(map)
#         terminal_clear()

#     def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
#         pass

#     def terminate(self) -> None:
#         pass


# from input import read_map_file

# if __name__ == "__main__":

#     # file_name = "maps/easy/01_linear_path.txt"
#     file_name = "maps/hard/01_maze_nightmare.txt"
#     # file_name = "maps/challenger/01_the_impossible_dream.txt"

#     drone_map = read_map_file(file_name)

#     visualizer = WindowedVisualizer(drone_map)

#     run = True

#     while run:

#         # Iterating over all the events received from
#         # pygame.event.get()
#         for event in pygame.event.get():

#             # If the type of the event is quit
#             # then setting the run variable to false
#             if event.type == pygame.QUIT:
#                 print("Quit")
#                 run = False

#     visualizer.terminate()
