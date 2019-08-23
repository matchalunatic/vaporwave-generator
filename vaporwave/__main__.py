import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from . import shapes
import logging
import sys
import math

the_args = sys.argv[1:]


logging.basicConfig(level=logging.DEBUG)

GRAY = (30, 30, 30)
SCREEN_SIZE = (1200, 900)
TRIANGLE_SIZE = (700, int(700 / 1.622))
TRIANGLE_SIZE_2 = (400, 400)
GRID_SIZE = (800, 600)



# positions
TOP_LEFT = (0, 0)
TOP_RIGHT = (SCREEN_SIZE[0], 0)
TOP_MIDDLE = (SCREEN_SIZE[0] / 2, 0)
MIDDLE_LEFT = (0, SCREEN_SIZE[1] / 2)
MIDDLE_RIGHT = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
MIDDLE_MIDDLE = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
BOTTOM_LEFT = (0, SCREEN_SIZE[1])
BOTTOM_MIDDLE = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1])
BOTTOM_RIGHT = (SCREEN_SIZE[0], SCREEN_SIZE[1])

MIDDLE_BOTTOM_3D = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1], 0)
MIDDLE_2THIRDS_3D = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 3 * 2, 0)
MIDDLE_MIDDLE_3D = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2, 0)


MIDDLE_MIDDLE_V2 = Vector2(MIDDLE_MIDDLE)

TENTEN_V2 = Vector2(10, 10)
UNITXY_V3 = Vector3(1, 1, 0)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption('w u t  i s  t h i s')
pygame.mouse.set_visible(0)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(GRAY)

screen.blit(background, (0, 0))
pygame.display.flip()


def researcher():
    step = +0.0001
    start = 0
    while True:
        yield Vector3(math.pi/6, 0, 0)
        start -= step

NULL_V3_GEN = shapes.default_number_generator(Vector3(0, 0, 0))
NULL_V2_GEN = shapes.default_number_generator(Vector2(0, 0))

UNIT_X_V2_GEN = shapes.default_number_generator(Vector2(1, 0))
UNIT_Y_V2_GEN = shapes.default_number_generator(Vector2(0, 1))
UNIT_X_V3_GEN = shapes.default_number_generator(Vector3(1, 0, 0))
UNIT_Y_V3_GEN = shapes.default_number_generator(Vector3(0, 1, 0))
UNIT_Z_V3_GEN = shapes.default_number_generator(Vector3(0, 0, 1))

COLOR_RED = (255, 0, 0, 255)
COLOR_GREEN = (0, 255, 0, 255)

sinw = lambda: shapes.sin_wave_angular_speed_generator(mul=60, speed=1, baseline=0.5)

halfer = lambda x: list(a/2 for a in x)

gene = lambda x: shapes.default_number_generator(x)
v2tov3 = lambda x: Vector3(x[0], x[1], 0)

tri = shapes.InfiniteTriangle(
        base_size=TRIANGLE_SIZE,
        num_triangles=7,
        generators={
            'color_generator': shapes.default_color_generator(
                (255, 0, 10, 255)),
            'zoom_generator': shapes.amplifier(
                shapes.default_zoom_generator(), 0.2),
            'alpha_angle_generator': sinw(),
            }
        )

tri.rect.center = screen.get_rect().center
tri.debug = False

tx, ty = TRIANGLE_SIZE_2
tri2 = shapes.InfiniteTriangle3D(
        base_size=TRIANGLE_SIZE_2, num_triangles=40,
        generators={
            'center3d_generator': gene(Vector3(tx/2, ty/2, 0)),
            'color_generator': shapes.default_color_generator(color=COLOR_GREEN),
            'zoom_generator': gene(1),
            'alpha_angle_generator': shapes.infinite_grower(step=-1),
            'beta_angle_generator': gene(0), # shapes.infinite_grower(step=-1),
            'gamma_angle_generator': gene(0),
            'translation_generator': gene(UNITXY_V3*300),
            'cam_center_generator': gene(Vector3(tx/2, ty/2, -400)), 
            'cam_angle_generator': NULL_V3_GEN,
            'cam_screen_generator': gene(Vector3(0, 0, 400)), # shapes.camera_generator(Vector3(0, 0, 1), Vector3(0, 0, 50), max_z=2000), #gene(Vector3(0, 0, 200)),
            'cam_aspect_ratio_generator': gene(1), 
            }
        )
tri2.rect.center = screen.get_rect().center
# tri2.rect.bottom = screen.get_rect().bottom

grid = shapes.Grid(base_size=GRID_SIZE, generators={
    'color_generator': shapes.advanced_color_generator(r_gen=shapes.default_number_generator(255), a_gen=shapes.default_number_generator(60), change_after=10),
    'zoom_generator': shapes.sin_wave_angular_speed_generator(baseline=2.2, mul=2),
    'spacing_x_generator': shapes.sin_wave_angular_speed_generator(
        baseline=15, mul=1),
    'spacing_y_generator': shapes.cos_wave_angular_speed_generator(
        baseline=15, mul=1),
    'translation_generator': gene(TENTEN_V2),
},
)

grid.rect.center = MIDDLE_MIDDLE
grid.debug = False

grid2 = shapes.Grid3D(base_size=None, generators={
    'color_generator': shapes.advanced_color_generator(r_gen=shapes.default_number_generator(255), a_gen=shapes.default_number_generator(128), change_after=100),
    'zoom_generator': shapes.default_number_generator(1),
    'alpha_angle_generator': shapes.default_number_generator(0),
    'spacing_x_generator': shapes.default_number_generator(30),
    'spacing_y_generator': shapes.default_number_generator(30),
    'translation_generator': NULL_V3_GEN,
#    'cam_center_generator': gene(Vector3(600, 600, -100)),
    'cam_center_generator': shapes.camera_generator(Vector3(600, 600, -50), increment_vector=Vector3(0, -1, 0), min_y=300),
    'cam_angle_generator': gene(Vector3(math.pi/9, 0, 0)),
    'cam_screen_generator': gene(Vector3(0, 0, 200)),
    'center3d_generator': shapes.default_number_generator(
        [600, 450, 0]),
},
)

grid2.rect.center = MIDDLE_MIDDLE
#grid2.rect.center = BOTTOM_MIDDLE
clock = pygame.time.Clock()
#allsprites = pygame.sprite.Group((tri, tri2, grid2, grid))
allsprites = pygame.sprite.Group((tri2,))
#allsprites = pygame.sprite.Group((tri,))
#allsprites = pygame.sprite.Group((tri, grid))
#allsprites = pygame.sprite.Group((grid2,))


names = {
'tri': tri,
'tri2': tri2,
'grid': grid,
'grid2': grid2,
        }

elems = tuple(b for a, b in names.items() if a in the_args)

allsprites = pygame.sprite.Group(elems)


going = True

while going:
    clock.tick(25)
    for event in pygame.event.get():
        if event.type == QUIT:
            going = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            going = False

#
    allsprites.update()
    screen.blit(background, (0, 0))

    allsprites.draw(screen)
    pygame.display.update()


pygame.quit()
