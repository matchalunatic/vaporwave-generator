import pygame
from pygame.locals import *
from . import shapes

GRAY = (30, 30, 30)
SCREEN_SIZE = (1200, 900)
TRIANGLE_SIZE = (700, int(700 / 1.622))
TRIANGLE_SIZE_2 = (1000, 1000)
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


pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption('w u t  i s  t h i s')
pygame.mouse.set_visible(0)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(GRAY)

screen.blit(background, (0, 0))
pygame.display.flip()

tri = shapes.InfiniteTriangle(base_size=TRIANGLE_SIZE, num_triangles=4,
                              generators=dict(
                                  color_generator=shapes.default_color_generator(
                                      (255, 0, 10, 255)),
                                  zoom_generator=shapes.amplifier(
                                      shapes.default_zoom_generator(), 0.2),
                                  angular_speed_generator=shapes.sin_wave_angular_speed_generator(
                                      mul=2, speed=1, baseline=0.5)
                              )
                              )
tri.rect.center = screen.get_rect().center

tri2 = shapes.InfiniteTriangle3D(base_size=TRIANGLE_SIZE_2, num_triangles=13,
                                 generators=dict(
                                     center3d_generator=shapes.default_number_generator(
                                         [ TRIANGLE_SIZE_2[0]/2, TRIANGLE_SIZE_2[1]/2, 0]),
                                     color_generator=shapes.default_color_generator(
                                         color=(0, 255, 0)),
                                     zoom_generator=shapes.default_number_generator(
                                         0.3),
                                     beta_angular_speed_generator=shapes.default_number_generator(
                                         2),
                                     gamma_angular_speed_generator=shapes.default_number_generator(
                                         0)
                                 )
                                 )
tri2.rect.center = screen.get_rect().center

grid = shapes.Grid(base_size=GRID_SIZE, generators={
    'color_generator': shapes.advanced_color_generator(r_gen=shapes.default_number_generator(255), a_gen=shapes.default_number_generator(128), change_after=10),
    'zoom_generator': shapes.sin_wave_angular_speed_generator(baseline=5, mul=3),
    'spacing_x_generator': shapes.sin_wave_angular_speed_generator(
        baseline=15, mul=1),
    'spacing_y_generator': shapes.cos_wave_angular_speed_generator(
        baseline=15, mul=1)
},
)

grid.rect.center = screen.get_rect().center

grid2 = shapes.Grid3D(base_size=None, generators={
    'color_generator': shapes.advanced_color_generator(r_gen=shapes.default_number_generator(255), a_gen=shapes.default_number_generator(128), change_after=100),
    'zoom_generator': shapes.default_number_generator(1),
    # 'alpha_angular_speed_generator': shapes.iterable_looper((1,)*1000 + (-1,)*1000),
    'alpha_angular_speed_generator': shapes.series_generator([-90]),
    'spacing_x_generator': shapes.default_number_generator(30),
    'spacing_y_generator': shapes.default_number_generator(30),
    'center3d_generator': shapes.default_number_generator(
        [600, 450, 0]),
},
)

grid2.rect.center = MIDDLE_MIDDLE
#grid2.rect.center = BOTTOM_MIDDLE
clock = pygame.time.Clock()
allsprites = pygame.sprite.Group((tri, tri2, grid2))
#allsprites = pygame.sprite.Group((tri2,))
#allsprites = pygame.sprite.Group((tri, grid))
#allsprites = pygame.sprite.Group((grid2,))

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
#    screen.blit(tri.image, (0,0))
    pygame.display.update()


pygame.quit()
