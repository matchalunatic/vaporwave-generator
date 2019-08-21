import os
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
import math
from .utils import *


def init_generators(obj, generators=None):
    if generators is None:
        generators = {}
    angular_speed_generator = generators.pop('angular_speed_generator', None)
    color_generator = generators.pop('color_generator', None)
    width_generator = generators.pop('width_generator', None)
    zoom_generator = generators.pop('zoom_generator', None)
    alpha_generator = generators.pop('alpha_generator', None)
    if color_generator is None:
        color_generator = default_color_generator()
    if width_generator is None:
        width_generator = default_width_generator()
    if angular_speed_generator is None:
        angular_speed_generator = default_angular_speed_generator()
    if zoom_generator is None:
        zoom_generator = default_zoom_generator()
    if alpha_generator is None:
        alpha_generator = default_alpha_generator()
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
        init_generators(self, generators)
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

    def get_geometry(self):
        """return act_w, act_h, maxlen_x, maxlen_y, center"""
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = math.sqrt(act_w**2 + act_h**2)
        maxlen_y = maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(
            maxlen_y, self.screen_size[1])

        center = (maxlen_x // 2, maxlen_y // 2)
        return act_w, act_h, maxlen_x, maxlen_y, center

    def graff(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()

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


class PolygonSprite(pygame.sprite.Sprite):
    """This is a base class to help draw polygonal sprites"""

    def __init__(self, base_size=None, generators=None):
        if generators is None:
            generators = {}
        super(PolygonSprite, self).__init__()
        init_generators(self, generators)

        screen = pygame.display.get_surface()
        screen_size = scrw, scrh = screen.get_size()

        if base_size == None:
            base_size = screen_size
        base_w, base_h = base_size
        self.base_w = base_w
        self.base_h = base_h
        self.angle = 0 + next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.screen_size = screen_size
        super(PolygonSprite, self).__init__()
        self.rect = DummyRect()
        self.graff()

    def get_geometry(self):
        """return act_w, act_h, maxlen_x, maxlen_y, center"""
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = math.sqrt(act_w**2 + act_h**2)
        maxlen_y = maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(
            maxlen_y, self.screen_size[1])

        center = (maxlen_x // 2, maxlen_y // 2)
        return act_w, act_h, maxlen_x, maxlen_y, center

    def prepare_basic_shape(self):
        """This is a base class - children should spit out their polys here"""
        return []

    def do_geometric_transform(self, polys_in):
        """this is an identity transform"""
        return polys_in

    def graff(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()

        polys = self.prepare_basic_shape()
        polys = self.do_geometric_transform(polys)

        surface = pygame.Surface((maxlen_x, maxlen_y), pygame.SRCALPHA, 32)
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
        self.angle += next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.alpha = next(self.alpha_generator)
        super(PolygonSprite, self).update()
        self.graff()


# class InfiniteTriangle(pygame.sprite.Sprite):
class InfiniteTriangle(PolygonSprite):
    """Symmetric triangles
           A

       B       C
    """

    def __init__(self, base_size=None, min_w=30, num_triangles=42, generators=None):
        self.min_w = min_w
        self.num_triangles = num_triangles
        super(InfiniteTriangle, self).__init__(base_size, generators)

    def get_geometry(self):
        """return act_w, act_h, maxlen_x, maxlen_y, center"""
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = math.sqrt(act_w**2 + act_h**2)
        maxlen_y = maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(
            maxlen_y, self.screen_size[1])

        center = (maxlen_x // 2, maxlen_y // 2)
        return act_w, act_h, maxlen_x, maxlen_y, center

    def prepare_basic_shape(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
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
            polys.append(points)
        return polys

    def do_geometric_transform(self, polys_in):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        polys = []
        for points in polys_in:
            points = rotate_polygon_with_center(points, center, self.angle)
            points = scale_polygon_with_center(points, center, self.zoom)
            polys.append(points)
        return polys

    def update(self):
        super(InfiniteTriangle, self).update()


class InfiniteTriangle3D(InfiniteTriangle):

    def update(self):
        super(InfiniteTriangle3D, self).update()
        self.alpha_angle += next(self.alpha_angular_speed_generator)
        self.beta_angle += next(self.beta_angular_speed_generator)
        self.gamma_angle += next(self.gamma_angular_speed_generator)

    def __init__(self, base_size=None, min_w=30, num_triangles=42, generators=None):
        if generators is None:
            generators = {}
        alpha_angular_speed_generator = generators.pop(
            'alpha_angular_speed_generator', None)
        beta_angular_speed_generator = generators.pop(
            'beta_angular_speed_generator', None)
        gamma_angular_speed_generator = generators.pop(
            'gamma_angular_speed_generator', None)
        if alpha_angular_speed_generator is None:
            alpha_angular_speed_generator = default_number_generator(0)
        if beta_angular_speed_generator is None:
            beta_angular_speed_generator = default_number_generator(0)
        if gamma_angular_speed_generator is None:
            gamma_angular_speed_generator = default_number_generator(0)
        self.alpha_angular_speed_generator = alpha_angular_speed_generator
        self.beta_angular_speed_generator = beta_angular_speed_generator
        self.gamma_angular_speed_generator = gamma_angular_speed_generator
        self.alpha_angle = 0
        self.beta_angle = 0
        self.gamma_angle = 0
        super(InfiniteTriangle3D, self).__init__(
            base_size, min_w, num_triangles, generators)

    def do_geometric_transform(self, polys_in):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        center3D = Vector3(center[0], center[1], 0)
        polys = []
        for points in polys_in:
            # points = rotate_polygon_with_center(points, center, self.angle)
            points = scale_polygon_with_center(points, center, self.zoom)
            points = rotate3D_points_with_center(
                points, center3D, self.alpha_angle, self.beta_angle, self.gamma_angle)
            points = project_v3s_on_viewport(points)
            polys.append(points)
        return polys
