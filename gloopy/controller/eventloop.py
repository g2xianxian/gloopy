from __future__ import division
import logging

from euclid import Vector3

import pyglet
from pyglet.window import Window

from ..model.item.gameitem import GameItem
from ..model.move.orbit import Orbit
from ..view.render import Render
from ..util.vectors import origin, x_axis, y_axis, z_axis


log = logging.getLogger(__name__)


class Eventloop(object):

    def __init__(self, world, options):
        self.world = world
        self.options = options
        self.window = None
        self.fpss = []
        self.time = 0.0


    def init(self):
        log.info('init')
        self.window = Window(
            fullscreen=self.options.fullscreen,
            vsync=self.options.vsync,
            visible=False,
            resizable=True)

        self.camera = GameItem(
            position=Vector3(0, 0, 10),
            look_at=origin,
            update=Orbit(origin, 50, Vector3(2, 3, 1)),
        )
        self.world.add( self.camera )

        self.render = Render(self.window, self.camera, self.options)
        self.render.init()
        self.window.on_draw = lambda: self.render.draw(self.world)


    def start(self):
        log.info('start')
        pyglet.clock.schedule(self.update)
        self.window.set_visible()
        self.window.invalid = False
        pyglet.app.run()


    def update(self, dt):
        if self.options.print_fps:
            self.fpss.append(1/max(1e-6, dt))
        dt = min(dt, 1 / 30)
        self.time += dt

        self.world.update(self.time, dt)
        self.window.invalid = True


    def stop(self):
        log.info('stop')
        if self.window:
            self.window.close()
        if self.options.print_fps:
            print '  '.join("%6.1f" % (dt, ) for dt in self.fpss)

