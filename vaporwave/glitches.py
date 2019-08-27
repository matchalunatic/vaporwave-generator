import os
import math
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
import math
import logging
import traceback

logger = logging.getLogger(__name__)


class Glitch(pygame.sprite.Sprite):
    """A Glitch sprite, bound to another sprite: it will duplicate its content
       and glitch it somehow
    """

    def __init__(self, other_sprite):
        self.sprite_target = other_sprite
        super(Glitch, self).__init__()

    def update(self):
        self.image = self.sprite_target.image.copy()
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.glitch()

    def glitch(self):
        pass


class RGBPhaseGlitch(Glitch):
    def __init__(self, other_sprite, generators=None):
        if generators == None:
            generators = {}
        super(RGBPhaseGlitch, self).__init__(other_sprite)
        r_offset_x_generator = generators.pop('r_offset_x', default_number_generator(0))
        r_offset_y_generator = generators.pop('r_offset_y', default_number_generator(0))
        g_offset_x_generator = generators.pop('g_offset_x', default_number_generator(0))
        g_offset_y_generator = generators.pop('g_offset_y', default_number_generator(0))
        b_offset_x_generator = generators.pop('b_offset_x', default_number_generator(0))
        b_offset_y_generator = generators.pop('b_offset_y', default_number_generator(0))
        alpha_generator = generators.get('alpha', default_number_generator(20))
        self.r_offset_x_generator = r_offset_x_generator
        self.r_offset_y_generator = r_offset_y_generator
        self.g_offset_x_generator = g_offset_x_generator
        self.g_offset_y_generator = g_offset_y_generator
        self.b_offset_x_generator = b_offset_x_generator
        self.b_offset_y_generator = b_offset_y_generator
        self.alpha_generator = alpha_generator


    def update(self):
        self.r_offset_x = next(self.r_offset_x_generator)
        self.r_offset_y = next(self.r_offset_y_generator)
        self.g_offset_x = next(self.g_offset_x_generator)
        self.g_offset_y = next(self.g_offset_y_generator)
        self.b_offset_x = next(self.b_offset_x_generator)
        self.b_offset_y = next(self.b_offset_y_generator)
        self.alpha = next(self.alpha_generator)
        super(RGBPhaseGlitch, self).update()

    def glitch(self):
        par = pygame.surfarray.pixels_red(self.image).astype('uint32')
        par = numpy.roll(par, self.r_offset_x, 0)
        par = numpy.roll(par, self.r_offset_y, 1)
        pag = pygame.surfarray.pixels_green(self.image).astype('uint32')
        pag = numpy.roll(pag, self.g_offset_x, 0)
        pag = numpy.roll(pag, self.g_offset_y, 1)
        pab = pygame.surfarray.pixels_blue(self.image).astype('uint32')
        pab = numpy.roll(pab, self.b_offset_x, 0)
        pab = numpy.roll(pab, self.b_offset_y, 1)
        paa = numpy.full(self.rect[2:], fill_value=0xff, dtype=numpy.uint32)
        # this probably will not work on big endian
        pa_t = self.alpha << 24 | pag << 16 | par << 8  | pab << 0
        # remove blank alpha-only pixels
        pa_t = numpy.where(pa_t==self.alpha << 24, 0, pa_t)
        del(par, pab, pag, paa)
        pygame.surfarray.blit_array(self.image, pa_t)
        return
        #            pa[x + self.r_offset_x, y + self.r_offset_y] += pa[x, y] & 0xFF0000
        #            pa[x + self.r_offset_x, y + self.r_offset_y] += pa[x, y] & 0x00FF00
        #            pa[x + self.r_offset_x, y + self.r_offset_y] += pa[x, y] & 0x0000FF
