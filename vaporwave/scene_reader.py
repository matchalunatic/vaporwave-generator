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
from . import glitches as effects



import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3


logger = logging.getLogger(__name__)

Scene = namedtuple("Scene", 'title duration objects effects overall_effects music background_color')

class SceneReader(object):
    def __init__(self, scene_path):
        self._playing_music = None
        self.scene_path = scene_path
        self.parse_scene()
        self.init_pygame()
        self.populate_scene()
        self.mainloop()

    def parse_scene(self):
        with open(self.scene_path, 'r') as fh:
            data = yaml.load(fh, Loader=yaml.SafeLoader)
        self.data = data
        # parse global: section
        global_d = data.get('global', {})
        width = global_d.get('width', 1200)
        height = global_d.get('height', 900)
        title = global_d.get('title', 'default title')
        music = global_d.get('background_music', None)
        framerate = global_d.get('framerate', os.environ.get('FR', 25))
        self.background_color_generator = eval(str(global_d.get('background_color', 'utils.default_generator((0, 0, 0, 255))')), globals(), locals())
        self.default_background_color_generator = self.background_color_generator
        self.background_color = next(self.background_color_generator)
        self.width = width
        self.height = height
        self.title = title
        self.framerate = framerate
        self.background_music = music
        # parse objects: section

    def populate_scene(self):
        self.objects = {}
        self.effects = {}
        self.overall_effects = {}
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
            self.objects[objname] = obj
        feffects = data.get('effects', {})
        for objname, objdata in feffects.items():
            o_type = objdata.get('type', None)
            generators = objdata.get('generators', {})
            target_s = objdata.get('target', None)
            target = self.objects[target_s]
            if o_type not in dir(effects):
                raise RuntimeError("I do not know effect " + o_type)
            evalstr = "effects.{o_type}(other_sprite=target, generators=generators)".format(o_type=o_type)
        
            obj = eval(evalstr, globals(), locals())
            self.effects[objname] = obj
        fovreff = data.get('overall_effects', {})
        for objname, objdata in fovreff.items():
            o_type = objdata.get('type', None)
            generators = objdata.get('generators', {})
            target = self.screen_wrapper
            if o_type not in dir(effects):
                raise RuntimeError("I do not know effect " + o_type)
            evalstr = "effects.{o_type}(other_sprite=target, generators=generators)".format(o_type=o_type)
        
            obj = eval(evalstr, globals(), locals())
            self.overall_effects[objname] = obj
        for scene in data.get('scenes', []):
            title = scene.get('title', None)
            duration = scene.get('duration', 0)
            music = scene.get('music', None)
            scene_objlist = scene.get('objects', [])
            scene_efflist = scene.get('effects', [])
            scene_ovreflist = scene.get('overall_effects', [])
            scene_objs = tuple([self.objects[a] for a in scene_objlist])
            scene_effects = tuple([self.effects[a] for a in scene_efflist])
            scene_overall_effects = tuple([self.overall_effects[a] for a in scene_ovreflist])
            background_color = eval(str(scene.get('background_color', 'None')), globals(), locals())
            self.scenes.append(
                    Scene(
                        title=title, 
                        duration=duration,
                        objects=scene_objs,
                        effects=scene_effects,
                        overall_effects=scene_overall_effects,
                        music=music,
                        background_color=background_color)
                    )


    def parse_generators(self, generators):
        parsed = {}
        for gen, evalstr in generators.items():
            parsed[gen] = eval(str(evalstr), globals(), locals())
        return parsed

    def load_next_scene(self):
        if len(self.scenes) > self.scene_counter:
            self.current_stage.empty()
            self.overall_effects_stage.empty()
            cursc = self.scenes[self.scene_counter]
            logger.info("next scene: %s", cursc.title)
            if len(cursc.objects) > 0:
                self.current_stage.add(*cursc.objects)
            if len(cursc.effects) > 0:
                self.current_stage.add(*cursc.effects)
            if len(cursc.overall_effects) > 0:
                self.overall_effects_stage.add(*cursc.overall_effects)
            self.scene_counter += 1
            self.scene_title = cursc.title
            self.background_music = cursc.music
            if cursc.background_color is None:
                self.background_color_generator = self.default_background_color_generator
            else:
                self.background_color_generator = cursc.background_color
            self.update_title()
            self.update_music()
            return self.scene_counter
        else:
            self.scene_counter = 0
            return self.load_next_scene()

    def init_pygame(self):
        pygame.init()
        screen_size = (self.width, self.height)
        self.screen = pygame.display.set_mode(screen_size, 0, 32)
        self.current_stage = pygame.sprite.RenderUpdates([])
        self.overall_effects_stage = pygame.sprite.RenderUpdates([])
        self.clock = pygame.time.Clock()
        self.screen_wrapper = shapes.ScreenSurfaceWrapper(generators={'screen': self.screen})
        pygame.mixer.init()


    def update_music(self):
        if self.background_music == self._playing_music:
            return
        if self.background_music is None:
            pygame.mixer.music.stop()
            self._playing_music = None
            return
        pygame.mixer.music.set_volume(0.2)
        
        pygame.mixer.music.load(self.background_music)
        pygame.mixer.music.play()
        self._playing_music = self.background_music

    def update_title(self):
        pygame.display.set_caption(self.title.format(scene_title=self.scene_title))

    def mainloop(self):
        self.going = True
        self.load_next_scene()
        background = pygame.Surface(self.screen.get_size())
        background = background.convert_alpha()

        draw_over = False
        while self.going:
            self.background_color = next(self.background_color_generator)
            background.fill(self.background_color)
            self.clock.tick(self.framerate)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.going = False
                elif event.type == KEYDOWN and event.key == K_n:
                    self.load_next_scene()
                elif event.type == KEYDOWN and event.key == K_u:
                    draw_over = not draw_over
                elif event.type == KEYDOWN and event.key == K_s:
                    self.framerate = 1
                elif event.type == KEYDOWN and event.key == K_f:
                    self.framerate = 25
                elif event.type == KEYDOWN and event.key == K_t:
                    self.framerate = 250
            if not draw_over:
                self.screen.blit(background, (0, 0))
            self.current_stage.update()
            self.current_stage.draw(self.screen)
            self.overall_effects_stage.update()
            self.overall_effects_stage.draw(self.screen)
            pygame.display.update()
        pygame.quit()

