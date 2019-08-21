import os
import pygame
from pygame.locals import *
from pygame.math import Vector2
import math
from .utils import * 

class Triangle(pygame.sprite.Sprite):
    def __init__(self):
        super(Triangle, self).__init__()
        self.image, self.rect = load_image('triangle.png')

    def update(self):
        pass


class InfiniteTriangle(pygame.sprite.Sprite):
    """Symmetric triangles
           A
    
       B       C
    """
    def __init__(self, base_size=None, min_w=30, num_triangles=42, angular_speed_generator=None, color_generator=None, width_generator=None, zoom_generator=None):
        screen = pygame.display.get_surface()
        screen_size = scrw, scrh = screen.get_size()
        if color_generator is None:
            color_generator = default_color_generator()
        if width_generator is None:
            width_generator = default_width_generator()
        if angular_speed_generator is None:
            angular_speed_generator = default_angular_speed_generator()
        if zoom_generator is None:
            zoom_generator = default_zoom_generator()
        self.color_generator = color_generator
        self.width_generator = width_generator
        self.angular_speed_generator = angular_speed_generator 
        self.zoom_generator = zoom_generator
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
        #offset_top = (maxlen - act_h) / 2
        #offset_left = (maxlen - act_w) / 2
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
        self.angle += next(self.angular_speed_generator)
        self.zoom = next(self.zoom_generator)
        self.graff()

class InfiniteTriangleBitmap(Triangle):
    def __init__(self, init_size=None, smallest_w=10, num_triangles=20):
        super(InfiniteTriangle, self).__init__()
        screen = pygame.display.get_surface()
        if screen is None:
            raise RuntimeError("Initialize screen before creating an InfiniteTriangle")
        screen_size = scrw, scrh = screen.get_size()
        image_size = imgw, imgh = self.image.get_size()
        print(imgw, " ", imgh)
        if init_size is None:
            ratio = imgw // imgh
            init_size = (int(0.9 * scrw), int(0.9 * scrw * ratio))
        self.image = pygame.transform.scale(self.image, init_size)
        self.rect = self.image.get_rect()
        image_size = imgw, imgh = self.image.get_size()
        center = (imgw // 2, imgh // 2)
        surface = pygame.Surface(image_size)
        surface = surface.convert_alpha()
        surface.fill((255, 0, 0, 0))
        self.num_triangles = num_triangles
        # draw triangles on the surface from the largest to the smallest
        tri, _ = load_image('triangle.png')
        pixel_diff = imgw - smallest_w
        for idx in range(1, num_triangles + 1):
            ratio = idx / num_triangles
            print("ratio: ", ratio)
            # do not use division but rather set a step
            subsiz = (int(imgw * ratio), int(imgh * ratio))
            print(subsiz)
            subtri = pygame.transform.scale(tri, subsiz)
            pos = (center[0] - subsiz[0] // 2, center[1] - subsiz[1] // 2)
            surface.blit(subtri, pos)
        self.image, self.rect = surface, surface.get_rect()


class Grid(pygame.sprite.Sprite):
    def __init__(self):
        super(Triangle, self).__init__()
        self.image, self.rect = load_image('grid.png')

