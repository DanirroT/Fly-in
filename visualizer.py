from abc import ABC, abstractmethod

from map_classes import Zone
from map_classes import Coordinates, DroneMap

import pygame
import random


def terminal_clear() -> None:
    print("\033[H\033[J", end="")


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


class WindowedVisualizer(Visualizer):

    # screen
    dimensions: Coordinates

    def __init__(self, map: DroneMap) -> None:
        super().__init__(map)
        self.dimensions = Coordinates(600, 400)

        pygame.init()
        self.screen = pygame.display.set_mode(self.dimensions)
        pygame.display.set_caption("Fly-in")
        self.screen.fill((3, 20, 56))
        for _ in range(50):
            pygame.draw.circle(self.screen, (255, 255, 255),
                               [random.choice(range(self.dimensions.x)),
                                random.choice(range(self.dimensions.y))], 2, 0)
        self.build_map()
        pygame.display.update()

    def build_map(self) -> None:
        pass

    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pygame.display.update()

    def terminate(self) -> None:
        pygame.quit()


class TerminalVisualizer(Visualizer):

    def __init__(self, map: DroneMap) -> None:
        super().__init__(map)
        terminal_clear()

    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pass

    def terminate(self) -> None:
        pass


if __name__ == "__main__":
    visualizer = WindowedVisualizer()

    input()

    visualizer.terminate()
