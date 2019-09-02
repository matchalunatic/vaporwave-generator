import os
import math
import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from .utils import *
import math
import logging
import traceback

logger = logging.getLogger(__name__)


def transformation_rotation2d(object, points):
    act_w, act_h, maxlen_x, maxlen_y, center = object.get_geometry()
    angle = object.alpha_angle
    center = Vector2(object.base_w/2, object.base_h/2)
    out = []
    for point in points:
        point = Vector2(*point)
        relative_point = point - center
        relative_point = relative_point.rotate(angle)
        out.append(relative_point + center)
    return out


def enforce_v3(object, points):
    out = []
    for point in points:
        if len(point) == 2:
            point = Vector3(point[0], point[1], 0)
        out.append(point)
    return out


def transformation_rotation3d(object, points):
    out = []
    for point in points:
        if len(point) != 3:
            logger.error("Tried to perform a 3D transformation on a 2D point: %s (for %s)", point, object)
        cv = Vector3(*object.center3d)
        o = Vector3(point) - cv
        o = o.rotate_x(object.alpha_angle)
        o = o.rotate_y(object.beta_angle)
        o = o.rotate_z(object.gamma_angle)
        out.append(o + cv)
    return out


def transformation_translation3d(object, points):
    out = []
    for point in points:
        if len(point) != 3:
            logger.error("Tried to perform a 3D transformation on a 2D point: %s (for %s)", point, object)
        translation = object.translation
        if len(translation) != 3:
            logger.error("Tried to perform a 3D translation with a 2D translation_generator. Adjust! %s (for %s)", point, translation)
            translation = Vector3(translation[0], translation[1], 0)
        out.append(point + translation)
    return out
    

def transformation_zoom(object, points):
    """2D zoom transformation"""
    act_w, act_h, maxlen_x, maxlen_y, center = object.get_geometry()
    # get point coordinates relative to zoom
    center = Vector2(object.base_w/2, object.base_h/2)
    out = []
    for point in points:
        if len(point) != 2:
            logger.error("Tried to zoom a non-point: %s", point)
        rel_point = point - center
        # multiply said coordinates by zoom factor
        zf = object.zoom
        out.append(Vector2(*rel_point) * zf + center)
    return out


def transformation_zoom3d(object, points):
    """2D zoom transformation"""
    act_w, act_h, maxlen_x, maxlen_y, center = object.get_geometry()
    # get point coordinates relative to zoom
    out = []
#    min_x, max_z, min_y, max_y, min_z, max_z = getminmax_xyz(flatten(object.points))
    center = object.center3d
    for point in points:
        if len(point) != 3:
            logger.error("Tried to zoom a non-3D point: %s", point)
        rel_point = point - center
        # multiply said coordinates by zoom factor
        zf = object.zoom
        out.append(Vector3(*rel_point) * zf + center)
    return out



def transformation_translation(object, points):
    """2D translate"""
    out = []
    for point in points:
        if len(point) != 2:
            logger.error("Tried to do translation of a non-2D point: %s", point)
        translation = object.translation
        out.append(Vector2(*translation) + Vector2(*point))
    return out


def transformation_projection3d(object, points):
    return project_v3_camera(
            points,
            v3_cam=object.cam_center,
            v3_screen=object.cam_screen,
            v3_cam_angle=object.cam_angle,
            aspect_ratio=object.cam_aspect_ratio,
            )


def transformation_projection_offset(object, points):
    screen = pygame.display.get_surface()
    screen_size = scrw, scrh = screen.get_size()
    screen_center = Vector2(scrw/2, scrh/2)
    act_w, act_h, maxlen_x, maxlen_y, center = object.get_geometry()
    base_half_size = Vector2(object.base_size) / 2
    offset = screen_center -  base_half_size
    if object.is_3d:
        offset = screen_center

    out = []
    for point in points:
        out.append(point + offset)
    return out

class PipelinedSprite(pygame.sprite.Sprite):
    """Base class for all vaporwave-generator sprites
    
    """
    def build_surface_workflow(self):
        """Set all surfaces transformations"""
        self.surface_workflow = []


    def build_transform_workflow(self):
        self.transform_workflow = []

    def draw_surface(self):
        """Apply surface transformations"""
        for t in self.surface_workflow:
            self.image = t(self.image)
        self.rect = self.image.get_rect()
        # restore alpha channel
        self.image.convert_alpha()


    def populate_generators(self, generators):
        base_size = self.base_w, self.base_h
        color_generator = generators.pop('color', None)
        stroke_width_generator = generators.pop('stroke_width', None)
        zoom_generator = generators.pop('zoom', None)
        translation_generator = generators.pop('translation', None)
        alpha_generator = generators.pop('alpha', None)
        alpha_angle_generator = generators.pop('alpha_angle', None)
        rect_generator = generators.pop('rect', None)

        if color_generator is None:
            color_generator = default_color_generator()
        if stroke_width_generator is None:
            stroke_width_generator = default_width_generator()
        if zoom_generator is None:
            zoom_generator = default_zoom_generator()
        if translation_generator is None:
            translation_generator = default_number_generator(Vector2(0, 0))
        if alpha_generator is None:
            alpha_generator = default_alpha_generator()
        if alpha_angle_generator is None:
            alpha_angle_generator = default_number_generator(0)
        if rect_generator is None:
            rect_generator = default_generator(None)
        self.color_generator = color_generator
        self.stroke_width_generator = stroke_width_generator
        self.zoom_generator = zoom_generator
        self.translation_generator = translation_generator
        self.alpha_generator = alpha_generator
        self.rect_generator = rect_generator

        self.alpha_angle_generator = alpha_angle_generator

    def __init__(self, base_size, generators=None):
        """Initialize a PipelinedSprite"""
        if generators is None:
            generators = {}
        
        screen = pygame.display.get_surface()
        screen_size = scrw, scrh = screen.get_size()
        
        # if True: generate next color at each draw
        # otherwise: generate next color at each update
        self.color_per_draw = True
        # if True: generate next stroke width at each draw
        # otherwise: generate next stroke width at each update
        self.stroke_width_per_draw = False

        self.screen_size = screen_size
        base_w, base_h = base_size

        # these sizes should never be mutated
        self.base_w = base_w
        self.base_h = base_h
        

        # base color and stroke width

        self.populate_generators(generators)
        self.build_transform_workflow()
        self.build_surface_workflow()

        # populate basic properties
        self.color = next(self.color_generator)
        self.stroke_width = next(self.stroke_width_generator)


        if len(generators) > 0:
            logger.warning("Unhandled generators: %s", generators.keys())
            raise RuntimeError("Some generators remain unhandled")

        self.rect = DummyRect()
        self.keep_centered = False

        self.debug = False
        self.update()
        super(PipelinedSprite, self).__init__()

    def get_geometry(self):
        """return act_w, act_h, maxlen_x, maxlen_y, center"""
        act_w, act_h = self.zoom * self.base_w, self.zoom * self.base_h
        maxlen_x = act_w# math.sqrt(act_w**2 + act_h**2)
        maxlen_y = act_h# maxlen_x

        maxlen_x, maxlen_y = min(maxlen_x, self.screen_size[0]), min(
            maxlen_y, self.screen_size[1])

        s_w, s_h  = self.screen_size
        # center = (maxlen_x // 2, maxlen_y // 2)
        center = Vector2(s_w / 2, s_h / 2)
        return act_w, act_h, maxlen_x, maxlen_y, center

    def update(self):
        super(PipelinedSprite, self).update()
        self.zoom = next(self.zoom_generator)
        self.translation = next(self.translation_generator)
        self.alpha = next(self.alpha_generator)
        self.alpha_angle = next(self.alpha_angle_generator)
        if not self.color_per_draw:
            self.color = next(self.color_generator)
        if not self.stroke_width_per_draw:
            self.stroke_width = next(self.stroke_width_generator)
        self.draw_surface()
        self.update_position()
        wanted_rect = next(self.rect_generator)
        if wanted_rect is not None:
            self.rect = self.image.get_rect(**wanted_rect)

    def update_position(self):
        return
        self.rect.left = 0
        self.rect.top = 0

class GeometrySprite(PipelinedSprite):
    """Base class for all geometry based sprites
    
    
       This is for all sprites that that make use of pygame.draw to draw
       a basic geometric shape that will be redrawn over and over with varying
       parameters, endure many parameters transformations, ...
      
    """

    @property
    def is_3d(self):
        return False

    @property
    def draw_function(self):
        """This is a link to the actual draw function"""
        def _exc(surface, color, shape, width=1):
            raise RuntimeError("implement draw_function on a subclass!")
        return _exc

    @property
    def base_size(self):
        """helper to get a base_size tuple"""
        return self.base_w, self.base_h

    def populate_generators(self, generators):
        scrw, scrh = self.screen_size
        base_size = self.base_w, self.base_h
        beta_angle_generator = generators.pop(
            'beta_angle', None)
        gamma_angle_generator = generators.pop(
            'gamma_angle', None)
        center3d_generator = generators.pop(
            'center3d', None)
        cam_screen_generator = generators.pop(
            'cam_screen', None)
        cam_center_generator = generators.pop(
            'cam_center', None)
        cam_angle_generator = generators.pop(
            'cam_angle', None)
        cam_aspect_ratio_generator = generators.pop(
            'cam_aspect_ratio', None)


        if beta_angle_generator is None:
            beta_angle_generator = default_number_generator(0)
        if gamma_angle_generator is None:
            gamma_angle_generator = default_number_generator(0)
        if center3d_generator is None:
            center3D = Vector3(scrw // 2, scrh // 2, 0)
            center3d_generator = default_number_generator(center3D)
        if cam_screen_generator is None:
            cam_screen = Vector3(0, 0, max(base_size))
            cam_screen_generator = default_number_generator(cam_screen)
        if cam_center_generator is None:
            cam_center = Vector3(0, 0, 0)
            cam_center_generator = default_number_generator(cam_center)
        if cam_angle_generator is None:
            cam_angle = Vector3(0, 0, 0)
            cam_angle_generator = default_number_generator(cam_angle)
        if cam_aspect_ratio_generator is None:
            cam_aspect_ratio = 1
            cam_aspect_ratio_generator = default_number_generator(cam_aspect_ratio)

        self.beta_angle_generator = beta_angle_generator
        self.gamma_angle_generator = gamma_angle_generator
        self.center3d_generator = center3d_generator
        self.cam_screen_generator = cam_screen_generator
        self.cam_center_generator = cam_center_generator
        self.cam_angle_generator = cam_angle_generator
        self.cam_aspect_ratio_generator = cam_aspect_ratio_generator
        return super(GeometrySprite, self).populate_generators(generators)

    def build_transform_workflow(self):
        self.transform_workflow = [
            transformation_rotation2d,
            transformation_translation,
            transformation_zoom,
            transformation_projection_offset,
                ]

    def generate_points(self, points):
        """override this and populate a structured collection of points
           that can be used to feed pygame.draw.xxx
        """
        return list(points)

    def flatten_points(self):
        """A flattening function that prepares points for geometry transform
        
        This should return a flattened list of points upon which
        we will call transformative geometric functions
        """
        return flatten(self.points)

    def do_geometric_transform(self, points):
        """Call transformation workflow on given points"""
        # make a copy: we don't want inplace transforms
        points = list(points)
        for elem in self.transform_workflow:
            points = elem(self, points)
        return points

    def prepare_basic_shape(self):
        """Populate self.points with the basic form"""
        self.points = []

    def draw_surface(self):
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()

        self.prepare_basic_shape()
        points = self.do_geometric_transform(self.flatten_points())
        
        points = self.generate_points(points)

        surface_w, surface_h = maxlen_x, maxlen_y

        screen_size = self.screen_size
        surface = pygame.Surface(screen_size, pygame.SRCALPHA, 32)
        if self.debug:
            surface.fill((255, 255, 255, 30))
            mark_surface(surface)

        for drawable in points:
            if self.color_per_draw:
                self.color = next(self.color_generator)
            if self.stroke_width_per_draw:
                self.color = next(self.stroke_width_generator)
            if self.debug:
                logger.debug("%s -> draw", drawable)
            try:
                drawed = self.draw_function(surface, self.color, drawable, self.stroke_width)
            except TypeError as e:
                logger.error("Drawing error:\n%s", traceback.format_exc())
                logger.error("Parameters: surface %s color %s stroke_width %s drawable %s", surface, self.color, self.stroke_width, drawable)
                raise
        self.oldrect = self.rect
        self.image, self.rect = surface, surface.get_rect()
        # now call parent which will apply direct surface transforms
        super(GeometrySprite, self).draw_surface()
        
    def update(self):
        self.beta_angle = next(self.beta_angle_generator)
        self.gamma_angle = next(self.gamma_angle_generator)
        self.center3d = next(self.center3d_generator)
        self.cam_angle = next(self.cam_angle_generator)
        self.cam_screen = next(self.cam_screen_generator)
        self.cam_center = next(self.cam_center_generator)
        self.cam_aspect_ratio = next(self.cam_aspect_ratio_generator)
        super(GeometrySprite, self).update()
