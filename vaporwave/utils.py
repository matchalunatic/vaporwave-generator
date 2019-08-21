import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
import math
import numpy


_image_cache = {}


class DummyRect(object):
    center = [0, 0]


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


def load_image(name):
    img = _image_cache.get(name)
    if img is not None:
        return img, img.get_rect()
    fullname = os.path.join('assets', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        raise SystemExit(message)
    image = image.convert_alpha()
    _image_cache[name] = image
    return image, image.get_rect()


def default_color_generator(color=(128, 0, 0)):
    while True:
        yield color


def default_number_generator(num=10):
    while True:
        yield num





def tuple_minimal_total(minimum_value, a_tuple, intify=True, max_value=255):
    total = sum(a_tuple)
    if total >= minimum_value and not intify:
        return a_tuple
    difference = minimum_value - total
    out = list(a_tuple)
    while difference > 0:
        d = int(difference) % len(out)
        if out[d] < max_value:
            out[int(difference) % len(out)] += 1
        difference -= 1
    return tuple(int(o) for o in out)


def advanced_color_generator(change_after=None, r_gen=None, g_gen=None, b_gen=None, a_gen=None, booster=None):
    """Generates an infinite stream of RGBA colors"""
    if isinstance(change_after, int):
        change_after = default_number_generator(change_after)
    elif change_after is None:
        change_after = default_number_generator(10)
    if r_gen is None:
        r_gen = sin_wave_angular_speed_generator(
            baseline=127, mul=127, offset=math.pi/3)
    if g_gen is None:
        g_gen = sin_wave_angular_speed_generator(
            baseline=127, mul=127, offset=2*math.pi/3)
    if b_gen is None:
        b_gen = sin_wave_angular_speed_generator(
            baseline=127, mul=127, offset=math.pi)
    if a_gen is None:
        a_gen = default_number_generator(255)
    if booster is None:
        def booster(val): return tuple_minimal_total(80, val, intify=True)
    c = 0
    i = 0
    c_a = 0
    r, g, b, a = (0, 0, 0, 255)
    while True:
        if c_a == 0:
            r = next(r_gen)
            g = next(g_gen)
            b = next(b_gen)
            a = next(a_gen)
            c_a = next(change_after)
            col = booster((r, g, b, a))
        yield col
        c_a -= 1


def default_angular_speed_generator(speed=2):
    while True:
        yield speed


def default_width_generator(width=2):
    while True:
        yield width


def sin_wave_angular_speed_generator(mul=1, speed=1, baseline=0, offset=0):
    """Offset in rad"""
    i = 0
    while True:
        i += 1
        yield baseline + mul*math.sin(speed * i * math.pi / 180 + offset)


def cos_wave_angular_speed_generator(mul=1, speed=1, baseline=0, offset=0):
    """Offset in rad"""
    i = 0
    while True:
        i += 1
        yield baseline + mul*math.cos(speed * i * math.pi / 180 + offset)


def default_spacing_generator(spacing=10):
    while True:
        yield spacing


def default_zoom_generator(zoom_cycle=[0.6, 1, 3, 7, 2, 0.5, ], periods=[10, 30]):
    len_zooms = len(zoom_cycle)
    len_periods = len(periods)
    i = 1
    c = 0
    d = 0
    while True:
        i += 1
        if i % periods[d] == 0:
            c += 1
            c = c % len_zooms
            d += 1
            d = d % len_periods
        yield zoom_cycle[c]


def default_alpha_generator(alpha_cycle=[180, 255, 40, 62, 230, 100, ], periods=[10, 30, 20, 40, 20]):
    len_alpha = len(alpha_cycle)
    len_periods = len(periods)
    i = 1
    c = 0
    d = 0
    while True:
        i += 1
        if i % periods[d] == 0:
            c += 1
            c = c % len_alpha
            d += 1
            d = d % len_periods
        yield alpha_cycle[c]


def inverter(gen):
    while True:
        v = next(gen)
        if v == 0:
            yield 9999
        else:
            yield 1 / v


def negator(gen):
    while True:
        r = next(gen)
        yield -r


def amplifier(gen, amount=1):
    while True:
        v = next(gen)
        yield amount * v


def iterable_looper(iterable):
    while True:
        for i in iterable:
            yield i

def rotate_point_with_center(point, center, angle):
    """angle is in degrees"""
    px, py = point
    cx, cy = center
    rads = math.radians(angle)
    return (
        cx + (px - cx) * math.cos(rads) - (py - cy) * math.sin(rads),
        cy + (px - cx) * math.sin(rads) + (py - cy) * math.cos(rads),
    )


def scale_points_with_center(points, center, zoom):
    center = Vector2(*center)
    ret = list()
    for p in points:
        offset = p - center # center - p
        le = offset.length()
        offset.scale_to_length(le * zoom)
        ret.append(offset + center)
    return tuple(ret)


def rotate_points_with_center(points, center, angle):
    center = Vector2(*center)
    return tuple((center-p).rotate(angle) + center for p in points)


def rotate3D_point_with_center(point, center, alpha, beta, gamma):
    """
        rotate a set of points around three angles

    """
    if len(point) == 2:
        point = Vector3(point[0], point[1], 0)
    cv = Vector3(*center)
    # translate coordinates to center, rotate, and re-translate
    o = point - cv
    # rotate around the three angles
    o = o.rotate_x(alpha)
    o = o.rotate_y(beta)
    o = o.rotate_z(gamma)
    return o + cv 


def rotate3D_points_with_center(points, center, alpha, beta, gamma):
    """wrapper"""
    return [rotate3D_point_with_center(p, center, alpha, beta, gamma)
            for p in points]


def project_v3s_on_viewport(v3s, viewport=None):
    """wrapper"""
    return [project_v3_on_viewport(v3, viewport)
            for v3 in v3s]



def project_v3_on_viewport(v3, viewport=None):
    """This is a projection without perspective, for objects not in space"""
    if viewport is None:
        # this coordinate system is trivially resolved
        viewport = (
            Vector3(1, 0, 0),
            Vector3(0, 1, 0),
        )

    # get the Z unit vector
    normal = viewport[0].cross(viewport[1]).normalize()

    # now project the O->V3 vector onto the Z axis and re-vectorize
    # it by multiplying it by the unit vector
    z_proj = v3.dot(normal) * normal
    # now re-translate coordinates and we'll have screen coordinates
    p3d = v3 - z_proj
    o = Vector2(*p3d[0:2])
    return o


def project_v3_camera(v3_ps, v3_cam, v3_screen=None, v3_cam_angle=None, aspect_ratio=1):
    """Correct formula for perspective

       v3_ps: list of position of the points to be projected
       v3_cam: position of the camera
       v3_screen: position of the screen [default: (0;0;1)]
       v3_cam_angle: alpha, beta, gamma of camera [default 0;0;0)]

       I suck at matrices so I took the formulas from wikipedia
    """
    if v3_screen is None:
        v3_screen = Vector3(0, 0, 1)
    if v3_cam_angle is None:
        v3_cam_angle = Vector3(0, 0, 0)
    
    t_x, t_y, t_z = v3_cam_angle[:]
    e_x, e_y, e_z = v3_screen[:]
    c = lambda x: math.cos(x)
    s = lambda x: math.sin(x)
    cam_rot_mat_t_x = numpy.array([
            [1,     0,       0     ],
            [0,     c(t_x),  s(t_x)],
            [0,   -s(t_x),   c(t_x)],
        ])
    cam_rot_mat_t_y = numpy.array([
            [c(t_y),   0,   -s(t_y)],
            [0,        1,   0      ],
            [s(t_y),   0,   c(t_y) ],
        ])
    cam_rot_mat_t_z = numpy.array([
            [c(t_z),   s(t_z),    0],
            [-s(t_z),  c(t_z),    0],
            [0,        0,         1],
        ])

    screen_mat = numpy.array([
        [1,     0,      e_x/e_z],
        [0,     1,      e_y/e_z],
        [0,     0,      1/e_z]
    ])
    rotation = numpy.matmul(cam_rot_mat_t_x, cam_rot_mat_t_y)
    rotation = numpy.matmul(rotation, cam_rot_mat_t_z)

    out = []
    for v3_p in v3_ps:
        translated_p = numpy.array(list(v3_p - v3_cam))
        transformed_p = numpy.matmul(rotation, translated_p)
        homo_proj = numpy.matmul(screen_mat, transformed_p)
        if homo_proj[2] < 0.0001:
            homo_proj[2] = 0.0001
        proj_2d = Vector2(aspect_ratio * homo_proj[0] / homo_proj[2], homo_proj[1] / homo_proj[2])
        out.append(proj_2d)
    return out

    

def project_v3s_weak(v3s, origin, mul=100):
    out = []
    for v3 in v3s:
        r = project_v3_weak(v3, origin, mul)
        if r:
            out.append(r)
    return out


def project_v3_weak(v3, origin, mul=1):
    r = v3 - origin
    if r[2] == 0:
        return None
    res = Vector2(r[0]/r[2] * mul, r[1]/r[2] * mul) 
    return res


def series_generator(series, lastItem=0):
    for i in series:
        yield i
    while True:
        yield lastItem
        



def mark_surface(surf, message="here"):
    font = pygame.font.Font('freesansbold.ttf', 16)
    tl = font.render('TL ' + message, True, (255, 0, 0, 128), (0, 0, 255, 128))
    tr = font.render(message + ' TR', True, (255, 0, 0, 128), (0, 0, 255, 128))
    bl = font.render('BL ' + message , True, (255, 0, 0, 128), (0, 0, 255, 128))
    br = font.render(message + ' BR', True, (255, 0, 0, 128), (0, 0, 255, 128))
    surface_rect = surf.get_rect()
    tl_rect = tl.get_rect()
    tr_rect = tr.get_rect()
    bl_rect = bl.get_rect()
    br_rect = br.get_rect()
    tl_rect.top = surface_rect.top
    tl_rect.left = surface_rect.left
    tr_rect.top = surface_rect.top
    tr_rect.right = surface_rect.right
    bl_rect.bottom = surface_rect.bottom
    bl_rect.left = surface_rect.left
    br_rect.bottom = surface_rect.bottom
    br_rect.right = surface_rect.right
    surf.blit(tl, tl_rect)
    surf.blit(tr, tr_rect)
    surf.blit(bl, bl_rect)
    surf.blit(br, br_rect)
