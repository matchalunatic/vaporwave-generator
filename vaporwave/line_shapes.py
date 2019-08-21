import os
import math
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
import math


class LineSprite(pygame.sprite.Sprite):
    """Base class for line-based sprites"""
    def __init__(self, base_size=None, generators=None):
        screen = pygame.display.get_surface()
        screen_size = scrw, scrh = screen.get_size()
        if generators is None:
            generators = {}
        init_generators(self, generators)
        if base_size == None:
            base_size = screen_size
        base_w, base_h = base_size
        self.base_w = base_w
        self.base_h = base_h
        self.angle = 0 + next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.screen_size = screen_size
        super(LineSprite, self).__init__()
        self.rect = DummyRect()

    def get_geometry(self):
        """return act_w, act_h, maxlen_x, maxlen_y, center"""
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = math.sqrt(act_w**2 + act_h**2)
        maxlen_y = maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(
            maxlen_y, self.screen_size[1])

        center = (maxlen_x // 2, maxlen_y // 2)
        return act_w, act_h, maxlen_x, maxlen_y, center

    def do_geometric_transform(self, lines_in):
        """this is an identity transform"""
        return lines_in

    def graff(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()

        lines = self.prepare_basic_shape()
        lines = self.do_geometric_transform(lines)
        #maxlen_x *= 2
        #maxlen_y *= 2

        surface = pygame.Surface((maxlen_x, maxlen_y), pygame.SRCALPHA, 32)
        mark_surface(surface)
        for line in lines:
            if len(line) < 2:
                print("hey", line)
                continue
            try:
                pygame.draw.line(
                    surface, next(self.color_generator),
                    line[0], line[1],
                    next(self.width_generator))
            except TypeError as e:
                print("error:", e, line)
                raise
        surface.convert()
        oldrect = self.rect
        self.image, self.rect = surface, surface.get_rect()

        self.rect.center = oldrect.center

class Grid(LineSprite):
    """Infinite grid"""

    def __init__(self, base_size=None, generators=None):
        if generators is None:
            generators = {}

        spacing_x_generator = generators.pop('spacing_x_generator', None)
        spacing_y_generator = generators.pop('spacing_y_generator', None)
        if spacing_y_generator is None:
            spacing_y_generator = default_spacing_generator(10)
        if spacing_x_generator is None:
            spacing_x_generator = default_spacing_generator(10)
        self.spacing_x_generator = spacing_x_generator
        self.spacing_y_generator = spacing_y_generator
        super(Grid, self).__init__(base_size, generators)
        self.graff()

    def prepare_basic_shape(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        offset_top = (maxlen_y - self.base_h) / 2
        offset_left = (maxlen_x - self.base_w) / 2
        offset_vect = Vector2(offset_left, offset_top)
        spacing_y = next(self.spacing_y_generator)
        spacing_x = next(self.spacing_x_generator)
        line_count_h = int(maxlen_y // spacing_y) * 2
        line_count_v = int(maxlen_x // spacing_x) * 2
        lines = []
        for i in range(0, line_count_h):
            points = (
                (0, i * spacing_y),
                (maxlen_x * 2, i * spacing_y)
            )
            points = tuple(offset_vect + p for p in points)
            lines.append(points)
        for i in range(0, line_count_v):
            points = (
                Vector2(i * spacing_x, 0),
                Vector2(i * spacing_x, maxlen_y * 2)
            )
            points = tuple(offset_vect + p for p in points)
            lines.append(points)
        return lines

    def do_geometric_transform(self, lines_in):
        lines_in = super(Grid, self).do_geometric_transform(lines_in)
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        lines_out = []
        for points in lines_in:
            points = rotate_points_with_center(points, center, self.angle)
            points = scale_points_with_center(points, center, self.zoom)
            lines_out.append(points)
        return lines_out

    def update(self):
        super(Grid, self).update()
        self.angle += next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.alpha = next(self.alpha_generator)
        self.graff()


class Grid3D(Grid):
    def __init__(self, base_size=None, generators=None):
        if generators is None:
            generators = {}
        alpha_angular_speed_generator = generators.pop(
            'alpha_angular_speed_generator', None)
        beta_angular_speed_generator = generators.pop(
            'beta_angular_speed_generator', None)
        gamma_angular_speed_generator = generators.pop(
            'gamma_angular_speed_generator', None)
        center3d_generator = generators.pop(
            'center3d_generator', None)
        if alpha_angular_speed_generator is None:
            alpha_angular_speed_generator = default_number_generator(0)
        if beta_angular_speed_generator is None:
            beta_angular_speed_generator = default_number_generator(0)
        if gamma_angular_speed_generator is None:
            gamma_angular_speed_generator = default_number_generator(0)
        if center3d_generator is None:
            screen = pygame.display.get_surface()
            screen_size = scrw, scrh = screen.get_size()
            center3D = [scrw // 2, scrh // 2, 0]
            center3d_generator = default_number_generator(center3D)
        self.alpha_angular_speed_generator = alpha_angular_speed_generator
        self.beta_angular_speed_generator = beta_angular_speed_generator
        self.gamma_angular_speed_generator = gamma_angular_speed_generator
        self.center3d_generator = center3d_generator
        self.alpha_angle = 0
        self.beta_angle = 0
        self.gamma_angle = 0
        self.center3d = next(self.center3d_generator)
        # temporary
        self.camCenter = Vector3(600, -100, -400)
        super(Grid3D, self).__init__(
            base_size, generators)

    def do_geometric_transform(self, lines_in):
        # do not run Grid's GT
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        center3D = Vector3(*self.center3d)
        lines_out = []
        rotated = []
        for points in lines_in:
            points = scale_points_with_center(points, center, self.zoom)
            points = rotate3D_points_with_center(
                points, center3D, self.alpha_angle, self.beta_angle, self.gamma_angle)
            #points = project_v3s_on_viewport(points)
            #  points = project_v3s_weak(points, Vector3(1200, 900, -10), mul=0.02)
            points = project_v3_camera(
                    points,
                    v3_cam=self.camCenter,
                    v3_cam_angle=Vector3(-math.pi/3, 0, 0),
                    v3_screen=Vector3(0, 0, 350),
                    aspect_ratio=3
                    )
            lines_out.append(points)
        return lines_out

    def update(self):
        super(Grid3D, self).update()
        self.alpha_angle += next(self.alpha_angular_speed_generator)
        self.beta_angle += next(self.beta_angular_speed_generator)
        self.gamma_angle += next(self.gamma_angular_speed_generator)
        self.center3d = next(self.center3d_generator)
        # temporary
        self.camCenter += Vector3(0, 0, 1)
        if self.camCenter[2] > 0:
            self.camCenter[2] = -400
