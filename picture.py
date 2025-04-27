import os
try:
    import lib.color as color
except ModuleNotFoundError:
    import color

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

_DEFAULT_WIDTH = 512
_DEFAULT_HEIGHT = 512

class Picture:

    def __init__(self, arg1=None, arg2=None):

        if (arg1 is None) and (arg2 is None):
            maxW = _DEFAULT_WIDTH
            maxH = _DEFAULT_HEIGHT
            self._surface = pygame.Surface((maxW, maxH))
            self._surface.fill((0, 0, 0))
        elif (arg1 is not None) and (arg2 is None):
            fileName = arg1
            try:
                self._surface = pygame.image.load(fileName)
            except pygame.error:
                raise IOError()
        elif (arg1 is not None) and (arg2 is not None):
            maxW = arg1
            maxH = arg2
            self._surface = pygame.Surface((maxW, maxH))
            self._surface.fill((0, 0, 0))
        else:
            raise ValueError()

    def save(self, f):

        pygame.image.save(self._surface, f)

    def width(self):

        return self._surface.get_width()


    def height(self):

        return self._surface.get_height()

    def get(self, x, y):

        pygameColor = self._surface.get_at((x, y))
        return color.Color(pygameColor.r, pygameColor.g, pygameColor.b)



    def set(self, x, y, c):

        pygameColor = pygame.Color(c.getRed(), c.getGreen(), c.getBlue(), 0)
        self._surface.set_at((x, y), pygameColor)
