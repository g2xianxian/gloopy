import logging
from os.path import join

import ctypes
import numpy
from OpenGL import GL

import pyglet
from pyglet.event import EVENT_HANDLED
from pyglet.gl import gl_info

from .glyph import Glyph
from .modelview import ModelView
from .projection import Projection
from .shader import FragmentShader, ShaderProgram, VertexShader
from ..lib.euclid import Matrix4
from ..util import path
from ..util.color import Color
from ..util.gl import gl


log = logging.getLogger(__name__)


type_to_enum = {
    gl.GLubyte: gl.GL_UNSIGNED_BYTE,
    gl.GLushort: gl.GL_UNSIGNED_SHORT,
    gl.GLuint: gl.GL_UNSIGNED_INT,
}


def log_opengl_version():
    log.info('\n    '.join([
        'opengl:',
        gl_info.get_vendor(),
        gl_info.get_renderer(),
        gl_info.get_version(),
    ]) )
    

def matrix_to_ctypes(m):
    return (gl.GLfloat * 16)(
        m.a, m.e, m.i, m.m,
        m.b, m.f, m.j, m.n,
        m.c, m.g, m.k, m.o,
        m.d, m.h, m.l, m.p
    )


class Render(object):

    def __init__(self, window, camera, options):
        self.window = window
        self.projection = Projection(window)
        self.modelview = ModelView(camera)
        self.options = options
        self.clock_display = pyglet.clock.ClockDisplay()

    def init(self):
        log_opengl_version()
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_POLYGON_SMOOTH)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)

        gl.glCullFace(gl.GL_BACK)
        gl.glEnable(gl.GL_CULL_FACE)

        shader = ShaderProgram(
            VertexShader(join(path.DATA, 'shaders', 'lighting.vert')),
            FragmentShader(join(path.DATA, 'shaders', 'lighting.frag')),
        )
        shader.compile()
        shader.use()


    def drawable_items(self, world):
        '''
        Generator function, returns an iterator over all items in the world
        which have a glyph attribute. If an item doesn't have a glyph, but
        does have a shape, then we generate its glyph and include it in the
        iteration.
        '''
        for item in world:
            if not item.glyph:
                if item.shape:
                    item.glyph = Glyph.FromShape(item.shape)
                else:
                    continue
            yield item


    def draw(self, world):
        gl.glClearColor(*world.background_color.as_floats())
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.draw_items(self.drawable_items(world))
        if self.options.fps:
            self.draw_hud()
        self.window.invalid = False
        return EVENT_HANDLED


    def draw_items(self, items):
        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        self.projection.set_perspective(45)
        self.modelview.set_world()

        item = items.next()
        gl.glColorPointer(
            Color.NUM_COMPONENTS,
            gl.GL_UNSIGNED_BYTE,
            0,
            item.glyph.glcolors
        )
        gl.glNormalPointer(gl.GL_FLOAT, 0, item.glyph.glnormals)

        for item in items:
            gl.glPushMatrix()

            NUMPY = True
            if NUMPY:
                if not hasattr(item, 'matrix'):
                    matrix = item.orientation.get_matrix()
                    matrix[12:15] = item.position
                    # TODO: if we are to use numpy matrices properly (ie. use
                    # them to store positions and rotations) then I
                    # suspect 'matrix' needs to be be transposed, and the
                    # ctypes access to it below should un-transpose it.
                    #
                    # Using 'numpy_matrix.T' below has no effect, presumably
                    # numpy just sets a flag on the object or something,
                    # leaving the underlying storage unchanged. :-(
                    #
                    # or possibly that's just because 'numpy_matrix' is an
                    # array, not a matrix, so 'transposing' has no effect?
                    item.numpy_matrix = numpy.array(
                        matrix[:],
                        dtype=GL.GLfloat
                    )
                    item.matrix = \
                        numpy.ascontiguousarray(
                            item.numpy_matrix
                        ).ctypes.data_as(
                            ctypes.POINTER(gl.GLfloat)
                        )
                    print item.matrix[0]
                    print item.matrix[1]
                    print
                else:
                    if item.velocity:
                        item.numpy_matrix[12:15] += [
                            item.velocity.x / 100,
                            item.velocity.y / 100,
                            item.velocity.z / 100
                        ]
            else:
                if not hasattr(item, 'matrix'):
                    matrix = Matrix4()
                    if item.position is not None:
                        matrix.translate(*item.position)
                    if item.orientation is not None:
                        matrix *= item.orientation.get_matrix()
                    item.matrix = matrix_to_ctypes(matrix)

            if item.position or item.orientation:
                gl.glMultMatrixf(item.matrix)

            gl.glVertexPointer(
                Glyph.DIMENSIONS,
                gl.GL_FLOAT,
                0,
                item.glyph.glvertices
            )

            gl.glDrawElements(
                gl.GL_TRIANGLES,
                len(item.glyph.glindices),
                type_to_enum[item.glyph.glindex_type],
                item.glyph.glindices
            )
            gl.glPopMatrix()

        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)


    def draw_hud(self):
        self.projection.set_screen()
        self.modelview.set_identity()
        self.clock_display.draw()

