from .geom_base import *


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
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        spacing_x, spacing_y = self.spacing_x, self.spacing_y
        line_count_h = int(maxlen_y // spacing_y) 
        line_count_v = int(maxlen_x // spacing_x)
        lines = []
        for i in range(0, line_count_h):
            points = [
                Vector2(0, i * spacing_y),
                Vector2(maxlen_x, i * spacing_y)
            ]
            points = list(p for p in points)
            lines.append(points)
        for i in range(0, line_count_v):
            points = [
                Vector2(i * spacing_x, 0),
                Vector2(i * spacing_x, maxlen_y)
            ]
            lines.append(points)
        self.points = lines

    def update(self):
        self.spacing_x = next(self.spacing_x_generator)
        self.spacing_y = next(self.spacing_y_generator)
        super(Grid, self).update()


class Grid3D(Grid):
    def __init__(self, base_size=None, generators=None):
        if generators is None:
            generators = {}
        # temporary
        self.camCenter = Vector3(600, -100, -400)
        super(Grid3D, self).__init__(base_size,generators)

    def build_transform_workflow(self):
        self.transform_workflow = [
            enforce_v3,
            transformation_rotation3d,
            transformation_translation3d,
            transformation_projection3d,
        ]

    def update(self):
        # temporary
        self.camCenter += Vector3(0, 0, 1)
        if self.camCenter[2] > 0:
            self.camCenter[2] = -400
        super(Grid3D, self).update()
