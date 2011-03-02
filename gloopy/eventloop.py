from __future__ import division
import logging

from pyglet import app, clock
from pyglet.window import key, Window

from .view.render import Render
from .util.screenshot import screenshot


log = logging.getLogger(__name__)


class Eventloop(object):
    '''
    '''

    def __init__(self, world, camera, options):
        self.world = world
        self.camera = camera
        self.options = options

        self.window = None
        self.render = None
        self.fpss = []
        self.time = 0.0


    def init(self):
        log.info('init')
        self.window = Window(
            fullscreen=self.options.fullscreen,
            vsync=self.options.vsync,
            visible=False,
            resizable=True)
        self.render = Render(self.window, self.camera, self.options)
        self.render.init()
        self.window.on_draw = lambda: self.render.draw(self.world)
        self.window.on_key_press = self.on_key_press


    def start(self):
        log.info('start')
        clock.schedule(self.update)
        self.window.set_visible()
        self.window.invalid = False
        try:
            app.run()
            log.info('stop')
        except:
            log.error('abnormal stop')
        finally:
            if self.window:
                self.window.close()


    def update(self, dt):
        dt = min(dt, 1 / 30)
        self.time += dt
        self.world.update_all(self.time, dt)
        self.window.invalid = True


    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.window.dispatch_event('on_close')
        elif symbol == key.F12:
            self.options.fps = not self.options.fps
        elif symbol == key.ENTER and (modifiers & key.MOD_ALT):
            self.options.fullscreen = not self.options.fullscreen
            log.info('fullscreen: %s' % (self.options.fullscreen,))
            self.window.set_fullscreen(self.options.fullscreen)
        elif symbol == key.F9:
            screenshot()

