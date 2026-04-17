from abc import ABC, abstractmethod

from map_classes import Zone


class Visualizer(ABC):

    @abstractmethod
    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pass

    @abstractmethod
    def ___(self, start_zone: Zone, end_zone: Zone) -> None:
        pass


class WindowedVisualizer(Visualizer):

    def __init__(self) -> None:
        super().__init__()
        self.open_window()

    def open_window(self) -> None:
        pass

    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pass

    def ___(self, start_zone: Zone, end_zone: Zone) -> None:
        pass


class TerminalVisualizer(Visualizer):

    def __init__(self) -> None:
        super().__init__()
        print("\033[H\033[J", end="")

    def animate_turn(self, start_zone: Zone, end_zone: Zone) -> None:
        pass

    def ___(self, start_zone: Zone, end_zone: Zone) -> None:
        pass
