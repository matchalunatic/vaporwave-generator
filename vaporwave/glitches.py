import os
import math
import pygame
import random
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
import math
import logging
import traceback

logger = logging.getLogger(__name__)


def compose_colorarray(r, g, b, a):
    return a << 24 | g << 16 | r << 8  | b << 0


# https://stackoverflow.com/questions/20360675/roll-rows-of-a-matrix-independently/51613442
def indep_roll(arr, shifts, axis=1):
    """Apply an independent roll for each dimensions of a single axis.

    Parameters
    ----------
    arr : np.ndarray
        Array of any shape.

    shifts : np.ndarray
        How many shifting to use for each dimension. Shape: `(arr.shape[axis],)`.

    axis : int
        Axis along which elements are shifted.
    """
    arr = numpy.swapaxes(arr,axis,-1)
    all_idcs = numpy.ogrid[[slice(0,n) for n in arr.shape]]

    # Convert to a positive shift
    shifts[shifts < 0] += arr.shape[-1]
    all_idcs[-1] = all_idcs[-1] - shifts[:, numpy.newaxis]

    result = arr[tuple(all_idcs)]
    arr = numpy.swapaxes(result,-1,axis)
    return arr



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


class ConvergenceGlitch(RGBPhaseGlitch):
    def update(self):
        self.r_offset_x = 0
        self.g_offset_x = -6
        self.b_offset_x = 6
        self.r_offset_y = 0
        self.g_offset_y = 0
        self.b_offset_y = 0
        self.alpha = 255//3
        # skip parent method and go to grandparent
        super(RGBPhaseGlitch, self).update()

    def glitch(self):
        super(ConvergenceGlitch, self).glitch()
        self.sprite_target.image.blit(self.image, (0, 0))
        self.image = pygame.Surface((0, 0))
        self.rect = (0, 0)

class RandomCorruptionGlitch(Glitch):
    def __init__(self, other_sprite, generators=None):
        self.corruption_size = (64, 64)
        self.corruption_pixel_size = (8, 8)
        self.max_glitches = 12
        self.update_every_n = 25
        self.counter = 0
        self.corruptions_pos = []
        super(RandomCorruptionGlitch, self).__init__(other_sprite)

    def glitch(self):
        w, h = self.image.get_rect()[2:]
        c_w, c_h = self.corruption_size
        c_px, c_py = self.corruption_pixel_size
        c_size = c_ww, c_hh = c_w // c_px, c_h // c_py

        if self.counter % self.update_every_n == 0:
            self.corruptions_pos = []
            for _ in range(random.randint(0, self.max_glitches+1)):
                glitch_r = numpy.random.random_integers(0, 255, c_size).astype('uint32')
                glitch_g = numpy.random.random_integers(0, 255, c_size).astype('uint32')
                glitch_b = numpy.random.random_integers(0, 255, c_size).astype('uint32')
                glitch_a = numpy.random.random_integers(120, 255, c_size).astype('uint32')
                corr = compose_colorarray(glitch_r, glitch_g, glitch_b, glitch_a)
                corr = numpy.repeat(corr, c_px, axis=0)
                corr = numpy.repeat(corr, c_py, axis=1)
                g_x = random.randint(0, w-c_w-1)
                g_y = random.randint(0, h-c_h-1)
                self.corruptions_pos.append((g_x,g_y,corr))
        sur = pygame.surfarray.pixels2d(self.image)
        changed = False

        for pos in self.corruptions_pos:
            posx, posy, corruption = pos
            sur[posx:posx+c_w,posy:posy+c_h] = corruption
            #sur[pos[0]:pos[1] = corr
            changed = True
        if changed:
            pygame.surfarray.blit_array(self.image, sur)
        self.counter += 1


class LocalPermutationsGlitch(Glitch):
    def __init__(self, other_sprite, generators=None):
        self.corruption_size = (120, 8)
        self.max_glitches = 12
        super(LocalPermutationsGlitch, self).__init__(other_sprite)

    def glitch(self):
        w, h = self.image.get_rect()[2:]
        c_w, c_h = self.corruption_size
        sur = pygame.surfarray.pixels2d(self.image)
        for _ in range(random.randint(0, self.max_glitches+1)):
            g_x = random.randint(0, w-c_w-1)
            g_y = random.randint(0, h-c_h-1)
            numpy.random.shuffle(sur[g_x:g_x+c_w,g_y:g_y+c_h])
            

class ChunksPermutationsGlitch(Glitch):
    def __init__(self, other_sprite, generators=None):
        self.max_permutations = 20
        self.permutation_size = (128, 128)
        self.change_after = 50
        self.counter = 0
        self.permutations = []
        super(ChunksPermutationsGlitch, self).__init__(other_sprite)

    def glitch(self):
        self.image = pygame.Surface((0, 0))
        self.rect = (0, 0)
        w, h = self.sprite_target.image.get_rect()[2:]
        p_w, p_h = self.permutation_size
        sur = pygame.surfarray.pixels2d(self.sprite_target.image)
        if self.counter % self.change_after == 0:
            self.permutations = []
            for _ in range(random.randint(0, self.max_permutations + 1)):
                o_x = random.randint(0, w - p_w - 1)
                o_y = random.randint(0, h - p_h - 1)
                d_x = random.randint(0, w - p_w - 1)
                d_y = random.randint(0, h - p_h - 1)
                self.permutations.append((o_x, o_x + p_w, o_y, o_y + p_h, d_x, d_x + p_w, d_y, d_y + p_h))
        changed = True
        for p in self.permutations:
            obx, oex, oby, oey, dbx, dex, dby, dey = p
            o_chunk = sur[obx:oex, oby:oey] #.copy()
            d_chunk = sur[dbx:dex, dby:dey]
            # force alpha 255
            sur[obx:oex, oby:oey] = d_chunk
            sur[dbx:dex, dby:dey] = o_chunk
        else:
            changed = False
        if changed:
            # hide original by setting its alpha channel to 0
            # empty original sprite
            # self.sprite_target.image.fill((0, 0, 0, 0))
            # display glitched
            # pygame.surfarray.blit_array(self.image, sur)
            self.sprite_target.blit_array(self.sprite_target.image, sur)
        self.counter += 1
            

class SlightOffsetGlitch(Glitch):
    def __init__(self, other_sprite, generators=None):
        self.corruption_size = (64, 64)
        self.max_glitches = 12
        self.change_after = 13
        self.counter = 0
        self.offset_left = -3
        self.offset_top = 3
        self.permutations = []
        super(SlightOffsetGlitch, self).__init__(other_sprite)

    def glitch(self):
        self.image = pygame.Surface((0, 0))
        self.rect = (0, 0)
        w, h = self.sprite_target.image.get_rect()[2:]
        p_w, p_h = self.corruption_size
        sur = pygame.surfarray.pixels2d(self.sprite_target.image)
        if self.counter % self.change_after == 0:
            self.permutations = []
            for _ in range(random.randint(0, self.max_glitches + 1)):
                o_x = random.randint(abs(self.offset_left), w - p_w - 1 - abs(self.offset_left))
                o_y = random.randint(abs(self.offset_top), h - p_h - 1 - abs(self.offset_top))
                d_x = o_x + self.offset_left
                d_y = o_y + self.offset_top
                self.permutations.append((o_x, o_x + p_w,
                                          o_y, o_y + p_h,
                                          d_x, d_x + p_w,
                                          d_y, d_y + p_h))
        changed = True
        for p in self.permutations:
            obx, oex, oby, oey, dbx, dex, dby, dey = p
            o_chunk = sur[obx:oex, oby:oey] #.copy()
            d_chunk = sur[dbx:dex, dby:dey]
            # force alpha 255
            sur[obx:oex, oby:oey] = d_chunk
            sur[dbx:dex, dby:dey] = o_chunk
        else:
            changed = False
        if changed:
            # hide original by setting its alpha channel to 0
            # empty original sprite
            # self.sprite_target.image.fill((0, 0, 0, 0))
            # display glitched
            # pygame.surfarray.blit_array(self.image, sur)
            self.sprite_target.blit_array(self.sprite_target.image, sur)
        self.counter += 1


class WaveletGlitch(Glitch):
    """Make lines into wavelets"""
    def __init__(self, other_sprite, generators=None):
        self.amplitude_h = 1
        self.amplitude_v = 10
        # h line count for exploring all amplitudes (-a;+a)
        self.period_h = 30
        # v line count for exploring all amplitudes (-a;+a)
        self.period_v = 30
        self.permutations = []
        super(WaveletGlitch, self).__init__(other_sprite)

    def glitch(self):
        # blank self image
        self.image = pygame.Surface((0, 0))
        self.rect = (0, 0)
        # do the work
        w, h = self.sprite_target.image.get_rect()[2:]
        sur = pygame.surfarray.pixels2d(self.sprite_target.image)
        # generate horizontal offsets according to line
        col_multiplicators = [int(math.ceil(self.amplitude_h * numpy.cos(l / self.period_h * math.pi * 2))) + self.amplitude_h for l in range(len(sur[0]))]
        line_multiplicators = [int(math.ceil(self.amplitude_v * numpy.cos(l / self.period_h * math.pi * 2))) + self.amplitude_v for l in range(len(sur))]
        offsets_h = numpy.array(line_multiplicators)
        offsets_v = numpy.array(col_multiplicators)
        sur = indep_roll(sur, offsets_v, 0)
        sur = indep_roll(sur, offsets_h, 1)
        # blit to source sprite target
        pygame.surfarray.blit_array(self.sprite_target.image, sur)
