from .geom_base import *
from random import Random

class LineSprite(GeometrySprite):
    """Base class for line-based sprites"""
    def generate_points(self, points):
        if len(points) % 2 != 0:
            raise RuntimeError("odd number of points for LineSprite")
        g = iter(list(points))
        return list(zip(g, g))

    @property
    def draw_function(self):
        return lambda surface, color, shape, width=1: pygame.draw.line(surface, color, shape[0], shape[1], width)




class Rain(LineSprite):
    """Dots rain
    """
    def __init__(self, base_size=None, generators=None):
        if generators is None:
            generators = {}

        v_line_count = generators.pop('v_line_count', default_generator(25))
        v_spacing = generators.pop('v_spacing', default_generator(20))
        v_drops_count = generators.pop('v_drops_count', default_generator(13))
        v_distance_ratio = generators.pop('v_distance_ratio', default_generator(1))

        self.v_line_count_generator = v_line_count
        self.v_spacing_generator = v_spacing
        self.v_distance_ratio_generator = v_distance_ratio
        self.v_drops_count_generator = v_drops_count

        super(Rain, self).__init__(base_size, generators)

    def update(self):
        self.v_line_count = next(self.v_line_count_generator)
        self.v_spacing = next(self.v_spacing_generator)
        self.v_distance_ratio = next(self.v_distance_ratio_generator)
        self.v_drops_count = next(self.v_drops_count_generator)
        return super(Rain, self).update()

    def make_drop(self, x, y):
        """
            O
           OXO
            O
        """
        return [
                (
                 Vector2(x-1, y),
                 Vector2(x+1, y),
                ),
                (
                 Vector2(x, y-1),
                 Vector2(x, y+1),
                )
               ]

    def prepare_basic_shape(self):
        """Each rain drop is a starlet
           x
          xxx
           x
        """
        w, h = self.base_size
        
        offset = w / self.v_line_count
        self.points = []
        for col in range(self.v_line_count):
            x = col * offset
            for drop_i in range(self.v_drops_count):
                y_base = drop_i * self.v_spacing
                y = y_base ** self.v_distance_ratio 
                self.points.append(self.make_drop(x, y))
            

class Grid(LineSprite):
    """2D grid"""

    def __init__(self, base_size=None, generators=None):
        if generators is None:
            generators = {}

        spacing_x_generator = generators.pop('spacing_x', None)
        spacing_y_generator = generators.pop('spacing_y', None)
        if spacing_y_generator is None:
            spacing_y_generator = default_spacing_generator(10)
        if spacing_x_generator is None:
            spacing_x_generator = default_spacing_generator(10)
        self.spacing_x_generator = spacing_x_generator
        self.spacing_y_generator = spacing_y_generator
        super(Grid, self).__init__(base_size, generators)

    def prepare_basic_shape(self):
        # act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        base_w, base_h = self.base_size
        spacing_x, spacing_y = self.spacing_x, self.spacing_y
        line_count_v = math.ceil(base_w / spacing_x)
        line_count_h = math.ceil(base_h / spacing_y)
        line_len_v = base_h
        line_len_h = base_w
        lines = []
        for i in range(0, line_count_h):
            points = [
                Vector2(0, i * spacing_y),
                Vector2(line_len_h, i * spacing_y)
            ]
            points = list(p for p in points)
            lines.append(points)
        for i in range(0, line_count_v):
            points = [
                Vector2(i * spacing_x, 0),
                Vector2(i * spacing_x, line_len_v)
            ]
            lines.append(points)
        self.points = lines

    def update(self):
        self.spacing_x = next(self.spacing_x_generator)
        self.spacing_y = next(self.spacing_y_generator)
        super(Grid, self).update()

class StarField(LineSprite):
    """A collection of a generated starfield. Each star is a 3-px cross.
    """

    def __init__(self, base_size=None, generators=None):
        random_seed = generators.pop('random_seed', 2307198819051991)
        stars_count = generators.pop('stars_count', 250)
        self.stars_count = stars_count
        self.random = Random(random_seed)
        self.starfield = []
        super(StarField, self).__init__(base_size, generators)
        self.build_starfield()

    def build_starfield(self):
        starfield = []
        w, h = self.base_size
        r = self.random
        for i in range(self.stars_count):
            x, y = r.randint(1, w-1), r.randint(1, h-1)
            starfield.append((x, y))
        self.starfield = starfield

    def prepare_basic_shape(self):
        """Run just as needed"""
        if not self.starfield:
            self.points = []
            return
        if self.points:
            return self.points

        for x, y in self.starfield:
            # horizontal axis
            self.points.append([
                Vector2(x - 1, y),
                Vector2(x + 1, y),
            ])
            # vertical axis
            self.points.append(
            [
                Vector2(x, y - 1),
                Vector2(x, y + 1),
            ])
        return self.points


class Grid3D(Grid):
    @property
    def is_3d(self):
        return True

    def build_transform_workflow(self):
        self.transform_workflow = [
            enforce_v3,
            transformation_rotation3d,
            transformation_translation3d,
            transformation_projection3d,
            transformation_projection_offset,
        ]

