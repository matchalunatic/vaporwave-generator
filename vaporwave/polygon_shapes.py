import os
import math
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
from .geom_base import *
import math



class PolygonSprite(GeometrySprite):
    """This is a base class to help draw polygonal sprites"""
    @property
    def draw_function(self):
        return pygame.draw.polygon

    def generate_points(self, points):
        # retrieve which points belong to which poly
        # iterate over original array and replace the elements in them
        replace_items(self.points, points)
        return list(self.points)
    
class InfiniteTriangle(PolygonSprite):
    """Symmetric triangles
           A

       B       C
    """

    def __init__(self, base_size=None, min_w=30, num_triangles=42, generators=None):
        self.min_w = min_w
        self.num_triangles = num_triangles
        super(InfiniteTriangle, self).__init__(base_size, generators)

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

            points = [
                Vector2(a_x, a_y),
                Vector2(b_x, b_y),
                Vector2(c_x, c_y),
            ]
            if any(points[i] == points[j] and i != j for i in range(len(points)) for j in range(len(points))):
                continue
            points = [offset_vect + p for p in points]
            polys.append(points)
        self.points = polys


class InfiniteTriangle3D(InfiniteTriangle):

    def __init__(self, base_size=None, min_w=30, num_triangles=42, generators=None):
        self.camCenter = Vector3(600, -100, -400)
        super(InfiniteTriangle3D, self).__init__(
            base_size, min_w, num_triangles, generators)

    def build_transform_workflow(self):
        self.transform_workflow = [
            enforce_v3,
            transformation_rotation3d,
            transformation_translation3d,
            transformation_projection3d,
        ]

