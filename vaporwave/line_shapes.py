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



class Grid(LineSprite):
    """2D grid"""

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
