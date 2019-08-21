import os
import pygame
from pygame.locals import *
from pygame.math import Vector2
import math
from .utils import * 

def init_generators(obj,
             angular_speed_generator=None, color_generator=None,
             width_generator=None, zoom_generator=None,
             alpha_generator=None):
    if color_generator is None:
        color_generator = default_color_generator()
    if width_generator is None:
        width_generator = default_width_generator()
    if angular_speed_generator is None:
        angular_speed_generator = default_angular_speed_generator()
    if zoom_generator is None:
        zoom_generator = default_zoom_generator()
    if alpha_generator is None:
        alpha_generator= default_alpha_generator()
    obj.color_generator = color_generator
    obj.width_generator = width_generator
    obj.angular_speed_generator = angular_speed_generator 
    obj.zoom_generator = zoom_generator
    obj.alpha_generator = alpha_generator

class Grid(pygame.sprite.Sprite):
    """Infinite grid"""

    def __init__(self, base_size=None, spacing_x_generator=None, spacing_y_generator=None, generators=None):
        if generators is None:
            generators = {}
        init_generators(self, **generators)
        screen = pygame.display.get_surface()
        screen_size = scrw, scrh = screen.get_size()

        if base_size == None:
            base_size = screen_size
        base_w, base_h = base_size
        self.base_w = base_w
        self.base_h = base_h
        if spacing_y_generator is None:
            spacing_y_generator = default_spacing_generator(10)
        if spacing_x_generator is None:
            spacing_x_generator = default_spacing_generator(10)
        self.spacing_x_generator = spacing_x_generator
        self.spacing_y_generator = spacing_y_generator
        self.angle = 0 + next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.screen_size = screen_size
        super(Grid, self).__init__()
        self.rect = DummyRect()
        self.graff()

    def graff(self):
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = math.sqrt(act_w**2 + act_h**2) 
        maxlen_y = maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(maxlen_y, self.screen_size[1])

        center = (maxlen_x //2, maxlen_y // 2)
        surface = pygame.Surface((maxlen_x, maxlen_y), pygame.SRCALPHA, 32)
        polys = list()
        offset_top = (maxlen_y - self.base_h) / 2
        offset_left = (maxlen_x - self.base_w) / 2
        offset_vect = Vector2(offset_left, offset_top)
        spacing_y = next(self.spacing_y_generator)
        spacing_x = next(self.spacing_x_generator)
        line_count_h = int(maxlen_y // spacing_y)
        line_count_v = int(maxlen_x // spacing_x)
        lines = []
        for i in range(0, line_count_h):
            points = (
                    (0, i * spacing_y),
                    (maxlen_x, i * spacing_y)
                )
            points = tuple(offset_vect + p for p in points)
            points = rotate_polygon_with_center(points, center, self.angle)
            points = scale_polygon_with_center(points, center, self.zoom)
            lines.append(points)
        for i in range(0, line_count_v):
            points = (
                    Vector2(i * spacing_x, 0),
                    Vector2(i * spacing_x, maxlen_y)
                )
            points = tuple(offset_vect + p for p in points)
            points = rotate_polygon_with_center(points, center, self.angle)
            points = scale_polygon_with_center(points, center, self.zoom)
            lines.append(points)
        for line in lines:
            pygame.draw.line(
                    surface, next(self.color_generator),
                    line[0], line[1],
                    next(self.width_generator))
        surface.convert()
        oldrect = self.rect
        self.image, self.rect = surface, surface.get_rect()
        self.rect.center = oldrect.center

    def update(self):
        super(Grid, self).update()
        self.angle += next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.alpha = next(self.alpha_generator)
        self.graff()






class InfiniteTriangle(pygame.sprite.Sprite):
    """Symmetric triangles
           A
    
       B       C
    """


    def __init__(self, base_size=None, min_w=30, num_triangles=42, generators=None):
        if generators is None:
            generators = {}
        super(InfiniteTriangle, self).__init__()
        init_generators(self, **generators)

        screen = pygame.display.get_surface()
        screen_size = scrw, scrh = screen.get_size()

        if base_size == None:
            base_size = screen_size
        base_w, base_h = base_size
        self.base_w = base_w
        self.base_h = base_h
        self.min_w = min_w
        self.num_triangles = num_triangles
        self.angle = 0 + next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.screen_size = screen_size
        super(InfiniteTriangle, self).__init__()
        self.rect = DummyRect()
        self.graff()

    def graff(self):
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = math.sqrt(act_w**2 + act_h**2) 
        maxlen_y = maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(maxlen_y, self.screen_size[1])

        center = (maxlen_x //2, maxlen_y // 2)
        surface = pygame.Surface((maxlen_x, maxlen_y), pygame.SRCALPHA, 32)
        polys = list()
        offset_top = (maxlen_y - self.base_h) / 2
        offset_left = (maxlen_x - self.base_w) / 2
        offset_vect = Vector2(offset_left, offset_top)
        for idx in range(1, self.num_triangles + 1):
            ratio = idx / self.num_triangles / 2
            a_x = self.base_w // 2 - 1
            a_y = ratio * self.base_h - 1
            b_x = ratio * self.base_w - 1 
            b_y = self.base_h - (ratio * self.base_h) - 1
            c_x = self.base_w - (ratio * self.base_w) - 1
            c_y = self.base_h - (ratio * self.base_h) - 1

            points = (
                      Vector2(a_x, a_y),
                      Vector2(b_x, b_y),
                      Vector2(c_x, c_y),
                     )
            if any(points[i] == points[j] and i != j for i in range(len(points)) for j in range(len(points))):
                continue
            points = tuple(offset_vect + p for p in points)
            points = rotate_polygon_with_center(points, center, self.angle)
            points = scale_polygon_with_center(points, center, self.zoom)
            polys.append(points)
        for poly in polys:
            pygame.draw.polygon(
                    surface, next(self.color_generator),
                    poly,
                    next(self.width_generator))
        surface.convert()
        oldrect = self.rect
        self.image, self.rect = surface, surface.get_rect()
        self.rect.center = oldrect.center
                    
    def update(self):
        super(InfiniteTriangle, self).update()
        self.angle += next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.alpha = next(self.alpha_generator)
        self.graff()

