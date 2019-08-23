from .geom_base import *


class ArcSprite(GeometrySprite):
    """Base class for line-based sprites"""
    @property
    def rectangle(self):
        # generate a centered rectangle
        act_w, act_h, maxlen_x, maxlen_y, center = self.get_geometry()
        scw, sch = self.screen_size
        return pygame.Rect((scw - act_w) / 2, (sch - act_h) / 2, act_w, act_h)

    def generate_points(self, points):
        if len(points) % 2 != 0:
            raise RuntimeError("odd number of angles for ArcSprite")
        g = iter(list(points))
        return list(zip(g, g))

    @property
    def draw_function(self):
        """shape here must be: (start_angle, end_angle)"""
        rect = self.rectangle
        return lambda surface, color, shape, width=1: pygame.draw.arc(surface, color, rect, shape[0], shape[1], width)


    def build_transform_workflow(self):
        self.transform_workflow = [
        ]


class SingleGroove(ArcSprite):

    def __init__(self, base_size, generators=None):
        amplitude_start_generator = generators.pop('amplitude_start_generator', None)
        amplitude_end_generator = generators.pop('amplitude_end_generator', None)
        if amplitude_start_generator is None:
            amplitude_start_generator = default_number_generator(0)
        if amplitude_end_generator is None:
            amplitude_end_generator = default_number_generator(math.pi/3)

        self.amplitude_start_generator = amplitude_start_generator
        self.amplitude_end_generator = amplitude_end_generator

        super(SingleGroove, self).__init__(base_size, generators)

    def update(self):
        self.amplitude_start = next(self.amplitude_start_generator)
        self.amplitude_end = next(self.amplitude_end_generator)
        super(SingleGroove, self).update()

    def prepare_basic_shape(self):
        self.points = [self.amplitude_start + self.alpha_angle, self.amplitude_end + self.alpha_angle]

