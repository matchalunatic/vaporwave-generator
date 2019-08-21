import pygame
from pygame.locals import *
from . import shapes

GRAY = (30, 30, 30)
SCREEN_SIZE = (1200, 900)
TRIANGLE_SIZE = (700, int(700 / 1.622))
TRIANGLE_SIZE_2 = (1000, 1000)
GRID_SIZE = (800, 600)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption('w u t  i s  t h i s')
pygame.mouse.set_visible(0)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(GRAY)

screen.blit(background, (0, 0))
pygame.display.flip()

tri = shapes.InfiniteTriangle(base_size=TRIANGLE_SIZE, num_triangles=120,
                              generators=dict(
                                  color_generator=shapes.default_color_generator(
                                      (255, 0, 10, 255)),
                                  zoom_generator=shapes.amplifier(
                                      shapes.default_zoom_generator(), 20),
                                  angular_speed_generator=shapes.sin_wave_angular_speed_generator(
                                      mul=2, speed=1, baseline=0.5)
                              )
                              )
tri.rect.center = screen.get_rect().center

tri2 = shapes.InfiniteTriangle3D(base_size=TRIANGLE_SIZE_2, num_triangles=13,
                                 generators=dict(
                                     color_generator=shapes.default_color_generator(
                                         color=(0, 128, 128)),
                                     zoom_generator=shapes.inverter(
                                         shapes.negator(shapes.default_zoom_generator())),
                                     angular_speed_generator=shapes.negator(
                                         shapes.sin_wave_angular_speed_generator(mul=2, speed=1, baseline=0.5))
                                 )
                                 )
tri2 = shapes.InfiniteTriangle3D(base_size=TRIANGLE_SIZE_2, num_triangles=13,
                                 generators=dict(
                                     color_generator=shapes.default_color_generator(
                                         color=(0, 128, 128)),
                                     zoom_generator=shapes.default_number_generator(
                                         1),
                                     alpha_angular_speed_generator=shapes.default_number_generator(
                                         1),
                                     gamma_angular_speed_generator=shapes.default_number_generator(
                                         0.2)
                                 )
                                 )
tri2.rect.center = screen.get_rect().center

grid = shapes.Grid(base_size=GRID_SIZE, generators={
    'color_generator': shapes.advanced_color_generator(r_gen=shapes.default_number_generator(255), a_gen=shapes.default_number_generator(128), change_after=10),
    'zoom_generator': shapes.sin_wave_angular_speed_generator(baseline=5, mul=3),
},
    spacing_x_generator=shapes.sin_wave_angular_speed_generator(
        baseline=15, mul=1),
    spacing_y_generator=shapes.cos_wave_angular_speed_generator(
        baseline=15, mul=1)
)

grid.rect.center = screen.get_rect().center

clock = pygame.time.Clock()
allsprites = pygame.sprite.Group((tri, tri2, grid))
# allsprites = pygame.sprite.Group((tri2,))
#allsprites = pygame.sprite.Group((tri, grid))

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
