import pygame
from pygame.locals import *
from pygame.math import Vector2
import math


class DummyRect(object):
    center = [0, 0]


_image_cache = {}
def load_image(name):
    img = _image_cache.get(name)
    if img is not None:
        return img, img.get_rect()
    fullname = os.path.join('assets', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    _image_cache[name] = image
    return image, image.get_rect()


def default_color_generator(color=(128,0,0)):
    while True:
        yield color


def default_width_generator(width=1):
    while True:
        yield width


def default_angular_speed_generator(speed=2):
    while True:
        yield speed


def sin_wave_angular_speed_generator(mul=1, speed=1, baseline=0):
    i = 0
    while True:
        i += 1
        yield baseline + mul*math.sin(speed * i * math.pi / 180)


def default_zoom_generator(zoom_cycle=[0.6, 1, 3, 7, 2, 0.5,], periods=100):
    len_zooms = len(zoom_cycle)
    i = 1
    c = 0
    while True:
        i += 1
        if i % periods == 0:
            c += 1
            c = c % len_zooms
        yield zoom_cycle[c]
        

def rotate_point_with_center(point, center, angle):
    """angle is in degrees"""
    px, py = point
    cx, cy = center
    rads = math.radians(angle)
    return (
        cx + (px - cx) * math.cos(rads) - (py - cy) * math.sin(rads),
        cy + (px - cx) * math.sin(rads) + (py - cy) * math.cos(rads),
    )


def scale_polygon_with_center(points, center, zoom):
    center = Vector2(*center)
    ret = list()
    for p in points:
        offset = center - p
        le = offset.length()
        offset.scale_to_length(le * zoom)
        ret.append(offset + center)
    return tuple(ret)


def rotate_polygon_with_center(points, center, angle):
    center = Vector2(*center)
    return tuple((center-p).rotate(angle) + center for p in points)
