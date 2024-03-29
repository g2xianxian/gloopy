#! /usr/bin/env python
from __future__ import division
from random import randint, uniform

from pyglet.event import EVENT_HANDLED
from pyglet.window import key

# find gloopy in '../..', so we can run even if Gloopy is not installed
import fixpath

from gloopy import Gloopy
from gloopy.color import Color
from gloopy.geom.vector import Vector
from gloopy.geom.orientation import Orientation
from gloopy.gameitem import GameItem
from gloopy.move import Spinner, WobblySpinner, WobblyOrbit
from gloopy.move.cycle_frames import CycleFrames
from gloopy.shapes.cube import Cube, TruncatedCube, SpaceStation
from gloopy.shapes.cube_groups import (
    BitmapCubeCluster, CubeCross, CubeCorners, CubeGlob, RgbCubeCluster,
)
from gloopy.shapes.dodecahedron import Dodecahedron
from gloopy.shapes.extrude import extrude
from gloopy.shapes.icosahedron import Icosahedron
from gloopy.shapes.normalize import normalize
from gloopy.shapes.octahedron import Octahedron
from gloopy.shapes.ring import Ring, TriRings
from gloopy.shapes.shape import Shape
from gloopy.shapes.stellate import stellate
from gloopy.shapes.subdivide import subdivide
from gloopy.shapes.tetrahedron import Tetrahedron, DualTetrahedron
from gloopy.view.shape_to_glyph import shape_to_glyph


class KeyHandler(object):

    def __init__(self, world, render, camera):
        self.world = world
        self.world.update += self.world_update
        self.render = render
        self.camera = camera
        self.coaxials = set()

        self.keys = {
            key._1: lambda: self.add_shape(Tetrahedron(1, Color.Random())),
            key._2: lambda: self.add_shape(Cube(0.75, Color.Random())),
            key._3: lambda: self.add_shape(Octahedron(0.75, Color.Random())),
            key._4: lambda: self.add_shape(Dodecahedron(0.65, Color.Random())),
            key._5: lambda: self.add_shape(Icosahedron(0.4, Color.Random())),
            key._6: lambda: self.add_shape(DualTetrahedron(0.9, Color.Random())),
            key._7: lambda: self.add_shape( 
                SpaceStation(1.1),
                orientation=Orientation(),
                update=Spinner(
                    Vector.x_axis,
                    speed=1,
                    orientation=Orientation()
                ),
            ),
            key._0: self.add_triangle_square,

            key.Q: lambda: self.add_shape(
                CubeCross(0.67, Color.Red, Color.Red.tinted(Color.Orange)),
            ),
            key.W: lambda: self.add_shape(
                CubeCorners(
                    0.6, Color.Yellow.tinted(Color.White), Color.Yellow
                ),
            ),
            key.E: lambda: self.add_shape(
                Ring(Cube(0.5, Color.Green), 2, 20),
                orientation=Orientation(Vector.y_axis),
                update=Spinner(Vector.y_axis),
            ),
            key.R: lambda: self.add_shape(
                Ring(
                    TruncatedCube(1.75, 0.8, Color.SeaGreen, Color.Periwinkle),
                    6, 25
                ),
                update=Spinner(axis=Vector.x_axis, speed=0.5),
            ),
            key.T: lambda: self.add_shape(
                TriRings(Cube(1.02, Color.DarkTeal), 8, 40),
                update=WobblySpinner(speed=-0.2),
            ),
            key.Y: lambda: self.add_shape(
                shape=TriRings(Octahedron(5, Color.Teal), 12, 8),
                update=WobblySpinner(speed=-1),
            ),
            key.U: self.add_coaxial_rings,

            key.Z: lambda: self.add_shape(
                CubeGlob(4, 70, 1000, Color.DarkRed)
            ),
            key.X: lambda: self.add_shape(
                CubeGlob(8, 150, 2000, Color.Red)
            ),
            key.C: lambda: self.add_shape(
                RgbCubeCluster(16, 4000, scale=2, hole=70)
            ),
            #key.V: self.add_koche_tetra,

            key.V: lambda: self.add_shape(
                [
                    BitmapCubeCluster('invader1.png', edge=10),
                    BitmapCubeCluster('invader2.png', edge=10)
                ],
                position=Vector.RandomShell(350),
                update=CycleFrames(1),
            ),

            key.BACKSPACE: self.remove,
            key.F11: self.toggle_backface_culling,
            key.UP: lambda: self.camera_orbit(0.5),
            key.DOWN: lambda: self.camera_orbit(2.0),
            key.PAGEUP: lambda: self.camera_orbit(0.5),
            key.PAGEDOWN: lambda: self.camera_orbit(2.0),
        }
        self.keys_shift = {
            key.A: lambda: self.set_faces_suffix(''),
            key.S: lambda: self.set_faces_suffix('subdivide-center'),
            key.D: lambda: self.set_faces_suffix('subdivide-corner'),
            key.E: lambda: self.set_faces_suffix('extrude-end'),
            key.R: lambda: self.set_faces_suffix('extrude-side'),
        }
        self.keys_ctrl = {
            key.N: self.mod_normalize,
            key.S: self.mod_subdivide,
            key.U: lambda: self.mod_stellate_in(-0.67),
            key.I: lambda: self.mod_stellate_in(-0.33),
            key.O: lambda: self.mod_stellate_out(0.5),
            key.P: lambda: self.mod_stellate_out(1),
            key.Q: lambda: self.mod_extrude(0.25),
            key.W: lambda: self.mod_extrude(0.5),
            key.E: lambda: self.mod_extrude(1),
            key.R: lambda: self.mod_extrude(2),
            key.T: lambda: self.mod_extrude(4),
            key.Y: lambda: self.mod_extrude(8),
            key.C: self.mod_color,
            key.X: self.mod_spin,
            key.M: self.mod_move,
            key.Z: lambda: self.mod_move(Vector(0, 20, 0)),
        }
        self.faces_suffix = ''
        self.camera_radius = 3


    def world_update(self, time, dt):
        if self.camera.update:
            rate = 3 * dt
            self.camera.update.radius += (
                self.camera_radius - self.camera.update.radius) * rate


    def on_key_press(self, symbol, modifiers):
        if modifiers & key.MOD_SHIFT:
            if symbol in self.keys_shift:
                self.keys_shift[symbol]()
                return EVENT_HANDLED
        elif modifiers & key.MOD_CTRL:
            if symbol in self.keys_ctrl:
                self.keys_ctrl[symbol]()
                return EVENT_HANDLED
        else:
            if symbol in self.keys:
                self.keys[symbol]()
                return EVENT_HANDLED

    def get_selected_item(self):
        if self.world.items:
            itemid = max(self.world.items.iterkeys())
            item = self.world[itemid]
            if item.glyph:
                return self.world[itemid]

    def add_shape(self, shape, **kwargs):
        item = GameItem(shape=shape, **kwargs)
        self.world.add(item)
        self.set_faces_suffix('')
        return item

    def remove(self):
        item = self.get_selected_item()
        if item:
            self.world.remove(item)


    def add_triangle_square(self):
        self.add_shape(
            Shape(
                vertices=[
                    #       x   y   z
                    Vector( 0,  2,  1), # p0
                    Vector(-1,  0,  1), # p1
                    Vector( 1,  0,  1), # p2
                    Vector( 1,  0, -1), # p3
                    Vector(-1,  0, -1), # p4
                ],
                faces=[
                    [0, 1, 2],    # triangle
                    [2, 1, 0],    # triangle
                    [1, 2, 3, 4], # square
                    [4, 3, 2, 1], # square
                ],
                colors=[Color.Red, Color.Red, Color.Yellow, Color.Yellow],
            )
        )
        
    def add_coaxial_rings(self):
        height = randint(-10, 11)
        radius = randint(3, 10)
        color1 = Color.Blue.tinted(Color.Grey, abs(height/10))
        color2 = Color.Blue.tinted(Color.White, abs(height/10))
        self.add_shape(
            shape=Ring(
                CubeCross(4, color1, color2),
                radius * 6, 
                int(radius * 5),
            ),
            position=Vector(0, height * 6, 0),
            orientation=Orientation(Vector.y_axis),
            update=Spinner(Vector.y_axis, speed=uniform(-1, 1)),
        )

    def add_koche_tetra(self):
        color1 = Color.Random()
        color2 = Color.Random()
        shape = Tetrahedron(1, color1)
        for i in range(6):
            subdivide(shape, color=color1.tinted(color2, i/5))
            stellate(shape, self.faces_endswith(shape, 'subdivide-center'), 1)
        return self.add_shape(shape)


    def set_faces_suffix(self, suffix):
        self.faces_suffix = suffix

    def faces_endswith(self, shape, suffix):
        return [
            index
            for index, face in enumerate(shape.faces)
            if face.source.endswith(suffix)
        ]

    def mod_normalize(self):
        item = self.get_selected_item()
        normalize(item.shape)
        item.glyph = [shape_to_glyph(item.shape)]

    def mod_shape(self, modifier, *args):
        item = self.get_selected_item()
        faces = self.faces_endswith(item.shape, self.faces_suffix)
        modifier(item.shape, faces, *args)
        item.glyph = [shape_to_glyph(item.shape)]

    def mod_subdivide(self):
        self.mod_shape(subdivide)
        self.set_faces_suffix('subdivide-center')

    def mod_stellate_out(self, amount=1):
        self.mod_shape(stellate, amount)
        self.set_faces_suffix('stellate')

    def mod_stellate_in(self, amount=-0.33):
        self.mod_shape(stellate, amount)
        self.set_faces_suffix('stellate')

    def mod_extrude(self, length=1.0):
        self.mod_shape(extrude, length)
        self.set_faces_suffix('extrude-end')

    def recolor(self, shape, faces, color):
        for face_index in faces:
            shape.faces[face_index].color = color

    def mod_color(self):
        self.mod_shape(self.recolor, Color.Random())

    def mod_spin(self):
        item = self.get_selected_item()
        if isinstance(item.update, WobblySpinner):
            item.update = None
        else:
            item.update = WobblySpinner()

    def mod_move(self, offset=None):
        item = self.get_selected_item()

        if offset is None:
            offset = Vector.RandomShell(5)
        rate = 1

        def mover(item, time, dt):
            item.position = item.position + (offset- item.position) * rate * dt

        item.update = mover


    def toggle_backface_culling(self):
        self.render.backface_culling = not self.render.backface_culling

    def camera_orbit(self, factor):
        self.camera_radius *= factor


class Application(object):

    def __init__(self):
        self.gloopy = None

    def run(self):
        self.gloopy = Gloopy()
        self.gloopy.init()
        self.gloopy.world.background_color = Color.Orange
        self.gloopy.camera.update=WobblyOrbit(
            center=Vector.origin,
            radius=3,
            axis=Vector(2, -3, 1),
            angular_velocity=0.8,
            wobble_size=0.0,
            wobble_freq=0.01,
        )
        self.gloopy.camera.look_at = Vector(0, 0, 0)
        
        self.keyhandler = KeyHandler(
            self.gloopy.world,
            self.gloopy.render,
            self.gloopy.camera,
        )
        self.gloopy.window.push_handlers(self.keyhandler)

        self.gloopy.run()


if __name__ == '__main__':
    Application().run()

