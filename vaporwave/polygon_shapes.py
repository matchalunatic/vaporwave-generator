import os
import math
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
from .geom_base import *
import math
import copy



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
    
class Square(PolygonSprite):
    """Basic square"""
    def prepare_basic_shape(self):
        base_w, base_h = self.base_size
        contraction = 0
        self.points =[ [
                Vector2(contraction, contraction),
                Vector2(contraction, base_w-contraction),
                Vector2(base_w-contraction, base_h-contraction),
                Vector2(base_h-contraction, contraction),
                ] ]

class InfiniteTriangle(PolygonSprite):
    """Symmetric triangles
           A

       B       C
    """

    def __init__(self, base_size=None, min_w=None, num_triangles=None, generators=None):
        if not generators:
            generators = {}
        if min_w is None:
            min_w = generators.pop('min_w', 30)
        if num_triangles is None:
            num_triangles = generators.pop('num_triangles', 10)
        self.min_w = min_w
        self.num_triangles = num_triangles
        super(InfiniteTriangle, self).__init__(base_size, generators)

    def prepare_basic_shape(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        polys = list()
        for idx in range(0, self.num_triangles + 1):
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
    @property
    def is_3d(self):
        # special case here
        return False

    def build_transform_workflow(self):
        self.transform_workflow = [
            enforce_v3,
            # transformation_zoom3d,
            transformation_rotation3d,
            transformation_translation3d,
            transformation_projection3d,
            transformation_projection_offset,
        ]





class ObjSprite3D(PolygonSprite):
    """Load basic obj files

       For the moment polygonal faces are supported but not NURBS
    """

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path_dirty = True
        self._file_path = value

    def __init__(self, file_path, base_size=None, generators=None):
        self.file_path = file_path
        self._center3d = None
        super(ObjSprite3D, self).__init__(base_size, generators)

    @property
    def is_3d(self):
        return True

    def prepare_basic_shape(self):
        if not self._file_path_dirty:
            self.points = copy.deepcopy(self._points_source)
            return
        self.points = []
        vertices = []
        faces = []
        with open(self.file_path, 'r') as fh:
            lines = fh.readlines()
        for line in lines:
            line = line.split()
            if len(line) == 0:
                continue
            if line[0] == "v":
                vertices.append(v4_to_v3(line[1:]))
            elif line[0] == "f":
                fvs = [int(a.split('/')[0]) for a in line[1:]]
                face = []
                for i in fvs:
                    if i > 0:
                        i -= 1
                    face.append(vertices[i])
                faces.append(face)
        self._vertices = vertices
        self._points_source = copy.deepcopy(faces)
        self.points = faces
        self._file_path_dirty = False
        logger.debug("obj %s loaded", self.file_path)


    @property
    def center3d(self):
        if self._center3d is not None:
            return self._center3d
        min_x, max_x, min_y, max_y, min_z, max_z = getminmax_xyz(self._vertices)
        self.base_w, self.base_h, self.base_d = max_x - min_x, max_y - min_y, max_z - min_z
        self._center3d = Vector3(max_x-min_x, max_y-min_y, max_z-min_z) / 2 + Vector3(min_x, min_y, min_z)
        return self._center3d

    @center3d.setter
    def center3d(self, v):
        pass

    def build_transform_workflow(self):
       self.transform_workflow = [
            transformation_rotation3d,
            transformation_zoom3d,
            transformation_translation3d,
            transformation_projection3d,
            transformation_projection_offset,
        ]
