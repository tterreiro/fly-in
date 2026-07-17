import pygame


class RenderingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)


class GraphViz:
    @staticmethod
    def render(graph) -> None:
        screen = pygame.display.set_mode((800, 600))
        screen_size = screen.get_size()
        running = True
        while running:
            pass
