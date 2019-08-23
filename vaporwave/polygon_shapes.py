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
        for idx in range(1, self.num_triangles + 1):
            ratio = idx / self.num_triangles / 2
            a_x = self.base_w // 2 
            a_y = ratio * self.base_h 
            b_x = ratio * self.base_w 
            b_y = self.base_h - (ratio * self.base_h) 
            c_x = self.base_w - (ratio * self.base_w) 
            c_y = self.base_h - (ratio * self.base_h) 

            if a_y > b_y:
                continue
            points = [
                Vector2(a_x, a_y),
                Vector2(b_x, b_y),
                Vector2(c_x, c_y),
            ]
            if any(points[i] == points[j] and i != j for i in range(len(points)) for j in range(len(points))):
                continue
            polys.append(points)
        self.points = polys


class InfiniteTriangle3D(InfiniteTriangle):
    def build_transform_workflow(self):
        self.transform_workflow = [
            enforce_v3,
            transformation_rotation3d,
            transformation_translation3d,
            transformation_projection3d,
            transformation_projection_offset,
        ]
