#! /usr/bin/env python
from __future__ import division
import logging

from pyglet.event import EVENT_HANDLED
from pyglet.window import key

# let this script run within the 'examples' dir, even if Gloopy is not installed
import fixpath; fixpath

from gloopy import Gloopy
from gloopy.color import Color
from gloopy.geom.vector import origin, Vector
from gloopy.model.item.gameitem import GameItem
from gloopy.model.move import WobblyOrbit
from gloopy.shapes.shape import shape_to_glyph
from gloopy.shapes.cube import Cube
from gloopy.shapes.dodecahedron import Dodecahedron
from gloopy.shapes.icosahedron import Icosahedron
from gloopy.shapes.octahedron import Octahedron
from gloopy.shapes.tetrahedron import Tetrahedron, DualTetrahedron
from gloopy.shapes.normalize import normalize
from gloopy.shapes.subdivide import subdivide
from gloopy.shapes.stellate import stellate
#from gloopy.shapes.truncate import truncate


log = logging.getLogger(__name__)



class KeyHandler(object):

    def __init__(self, world):
        self.world = world
        self.bestiary = {
            key._1: self.add_tetrahedron,
            key._2: self.add_cube,
            key._3: self.add_octahedron,
            key._4: self.add_dodecahedron,
            key._5: self.add_icosahedron,
            key._6: self.add_dualtetrahedron,

            key.S: self.mod_subdivide,
            key.N: self.mod_normalize,
            key.O: self.mod_stellate_out,
            key.I: self.mod_stellate_in,

            key.U: self.mod_color_uniform,
            key.V: self.mod_color_variations,
            key.R: self.mod_color_random,
        }

    def on_key_press(self, symbol, modifiers):
        if symbol in self.bestiary:
            if modifiers & key.MOD_SHIFT:
                self.remove_by_symbol(symbol)
            else:
                self.bestiary[symbol](symbol)
            return EVENT_HANDLED

    def add_shape(self, shape, **kwargs):
        self.world.add(
            GameItem(
                shape=shape,
                **kwargs
            )
        )

    def add_tetrahedron(self, symbol):
        self.add_shape(Tetrahedron(1, Color.Random()), key=symbol)

    def add_cube(self, symbol):
        self.add_shape(Cube(1, Color.Random()), key=symbol)

    def add_octahedron(self, symbol):
        self.add_shape(Octahedron(1, Color.Random()), key=symbol)

    def add_dodecahedron(self, symbol):
        self.add_shape(Dodecahedron(1, Color.Random()), key=symbol)

    def add_icosahedron(self, symbol):
        self.add_shape(Icosahedron(1, Color.Random()), key=symbol)

    def add_dualtetrahedron(self, symbol):
        self.add_shape(DualTetrahedron(1, Color.Random()), key=symbol)


    def remove_by_symbol(self, symbol):
        to_remove = [
            item
            for item in self.world
            if item.key == symbol
        ]
        for item in to_remove:
            self.world.remove(item)

    def get_selected_item(self):
        if self.world.items:
            itemid = max(self.world.items.iterkeys())
            return self.world[itemid]

    def mod_shape(self, modifier):
        item = self.get_selected_item()
        modifier(item.shape)
        item.glyph = shape_to_glyph(item.shape)

    def mod_subdivide(self, _): self.mod_shape(subdivide)
    def mod_normalize(self, _): self.mod_shape(normalize)

    def stellate_out(self, shape): stellate(shape, 0.5)
    def stellate_in(self, shape): stellate(shape, -0.33)
    def mod_stellate_out(self, _): self.mod_shape(self.stellate_out)
    def mod_stellate_in(self, _): self.mod_shape(self.stellate_in)

    def mod_color(self, get_color):
        item = self.get_selected_item()
        for face in item.shape.faces:
            face.color = get_color()
        item.glyph = shape_to_glyph(item.shape)

    def mod_color_random(self, _):
        self.mod_color(Color.Random)

    def mod_color_uniform(self, _):
        c = Color.Random()
        self.mod_color(lambda: c)

    def mod_color_variations(self, _):
        self.mod_color(Color.Random().variations().next)


class Application(object):

    def __init__(self):
        self.gloopy = None

    def run(self):
        self.gloopy = Gloopy()
        self.gloopy.init()
        self.gloopy.world.background_color = Color.Orange
        self.gloopy.camera.update=WobblyOrbit(
            center=origin,
            radius=3,
            axis=Vector(2, -3, 1),
            angular_velocity=0.2,
            wobble_size=0.0,
            wobble_freq=1,
        )
        self.gloopy.camera.look_at = Vector(0, 0, 0)
        
        self.keyhandler = KeyHandler(self.gloopy.world)
        self.gloopy.eventloop.window.push_handlers(self.keyhandler)

        try:
            self.gloopy.start()
        finally:
            self.gloopy.stop()


if __name__ == '__main__':
    Application().run()

