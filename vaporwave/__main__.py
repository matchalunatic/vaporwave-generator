import pygame
from pygame.locals import *
from . import shapes

GRAY = (30, 30, 30)
SCREEN_SIZE = (1200, 900)
TRIANGLE_SIZE = (700, int(700 / 1.622))

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption('w u t  i s  t h i s')
pygame.mouse.set_visible(0)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(GRAY)

screen.blit(background, (0, 0))
pygame.display.flip()

tri = shapes.InfiniteTriangle(base_size=TRIANGLE_SIZE, num_triangles=20, angular_speed_generator=shapes.sin_wave_angular_speed_generator(mul=2, speed=1, baseline=0.5))
tri.rect.center = screen.get_rect().center

clock = pygame.time.Clock()
allsprites = pygame.sprite.Group((tri,))

going = True

while going:
    clock.tick(24)
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
