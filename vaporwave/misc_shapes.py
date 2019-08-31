import os
import math
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
from .geom_base import *
import math
import copy



class TextSprite(PipelinedSprite):
    def __init__(self, base_size=None, generators=None):
        text_generator = generators.pop('text', None)
        font = generators.pop('font', None)
        background = generators.pop('background', None)
        antialias = generators.pop('antialias', None)
        if text_generator is None:
            text_generator = iterable_stutterer(typewriter_iterator('please set a text'), stutter=5)
        if font is None:
            font = default_generator(('freesansbold.ttf', 8))
        if background is None:
            background = default_generator((0, 0, 0, 0))
        if antialias is None:
            antialias = default_generator(False)
        self.text_generator = text_generator
        self.font_generator = font
        self.background_generator = background
        self.antialias_generator = antialias
        self.image = pygame.Surface((200, 200))
        self.rect = self.image.get_rect()
        self._font_active = None
        super(TextSprite, self).__init__(base_size, generators)

    def update(self):
        self.font = next(self.font_generator)
        self.text = next(self.text_generator)
        self.background = next(self.background_generator)
        self.antialias = next(self.antialias_generator)
        super(TextSprite, self).update()

    def get_font(self):
        if self._font_active == self.font:
            return self._font_o
        font_o = pygame.font.Font(*self.font)
        self._font_o = font_o
        return self._font_o


    def build_surface_workflow(self):
        self.surface_workflow = [
            lambda x: pygame.transform.rotozoom(x, self.alpha_angle, self.zoom)
                ]

    def draw_surface(self):
        font_o = self.get_font()
        self.image = font_o.render(self.text, self.antialias, self.color, self.background)
        self.rect = self.image.get_rect()
        self.image.convert_alpha()
        return super(TextSprite, self).draw_surface()

