"""Vaporwave scenes reader

Cool for non-interactive scenes
"""

import os
import logging
import sys
import math

import yaml
from collections import namedtuple

from . import utils
from . import shapes
from . import glitches



import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3


Scene = namedtuple("Scene", 'title duration objects')

class SceneReader(object):
    def __init__(self, scene_path):
        self.scene_path = scene_path
        self.parse_scene()
        self.init_pygame()
        self.populate_scene()
        self.mainloop()

    def parse_scene(self):
        with open(self.scene_path, 'r') as fh:
            data = yaml.load(fh)
        self.data = data
        # parse global: section
        global_d = data.get('global', {})
        width = global_d.get('width', 1200)
        height = global_d.get('width', 900)
        title = global_d.get('title', 'default title')
        framerate = global_d.get('framerate', os.environ.get('FR', 25))
        self.background_color = eval(str(data.get('background_color', '(0, 0, 0, 255)')), globals(), locals())
        self.width = width
        self.height = height
        self.title = title
        self.framerate = framerate

        # parse objects: section

    def populate_scene(self):
        self.objects = {}
        self.scenes = []
        self.scene_counter = 0
        data = self.data
        fobjects = data.get('objects', {})
        for objname, objdata in fobjects.items():
            o_type = objdata.get('type', None)
            base_size = objdata.get('base_size', None)
            generators = objdata.get('generators', {})
            if base_size:
                base_size = tuple(base_size)
            generators = self.parse_generators(generators)
            if o_type not in dir(shapes):
                raise RuntimeError("I don't know shape " + o_type)
            evalstr = "shapes.{o_type}(base_size=base_size, generators=generators)".format(o_type=o_type)

            obj = eval(evalstr, globals(), locals())
            print(obj)
            self.objects[objname] = obj
        for scene in data.get('scenes', []):
            title = scene.get('title', None)
            duration = scene.get('duration', 0)
            scene_objlist = scene.get('objects')
            scene_objs = tuple([self.objects[a] for a in scene_objlist])
            self.scenes.append(Scene(title=title, duration=duration, objects=scene_objs))

        print(self.objects)

    def parse_generators(self, generators):
        parsed = {}
        for gen, evalstr in generators.items():
            parsed[gen] = eval(str(evalstr), globals(), locals())
        return parsed

    def load_next_scene(self):
        if len(self.scenes) > self.scene_counter:
            self.current_stage.empty()
            cursc = self.scenes[self.scene_counter]
            self.current_stage.add(*cursc.objects)
            self.scene_counter += 1
            return self.scene_counter
        else:
            self.scene_counter = 0
            return self.load_next_scene()

    def init_pygame(self):
        pygame.init()
        screen_size = (self.width, self.height)
        self.screen = pygame.display.set_mode(screen_size, 0, 32)
        pygame.display.set_caption(self.title)
        self.current_stage = pygame.sprite.RenderUpdates([])
        self.clock = pygame.time.Clock()



    def mainloop(self):
        self.going = True
        self.load_next_scene()
        background = pygame.Surface(self.screen.get_size())
        background = background.convert_alpha()

        background.fill(self.background_color)
        draw_over = False
        while self.going:
            self.clock.tick(self.framerate)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.going = False
                elif event.type == KEYDOWN and event.key == K_n:
                    print("next scene")
                    self.load_next_scene()
                elif event.type == KEYDOWN and event.key == K_u:
                    draw_over = not draw_over
            self.current_stage.update()
            if not draw_over:
                self.screen.blit(background, (0, 0))
            self.current_stage.draw(self.screen)
            pygame.display.update()
        pygame.quit()

