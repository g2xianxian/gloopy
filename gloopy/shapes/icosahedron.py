from __future__ import division
from math import sqrt

from .shape import Shape


def Icosahedron(size, colors):
    phi = (sqrt(5) + 1) / 2
    vertices = [
        ( phi/2,    0.5,    0.0), #0
        ( phi/2,   -0.5,    0.0), #1
        (-phi/2,   -0.5,    0.0), #2
        (-phi/2,    0.5,    0.0), #3
        (  -0.5,    0.0,  phi/2), #4
        (   0.5,    0.0,  phi/2), #5
        (   0.5,    0.0, -phi/2), #6
        (  -0.5,    0.0, -phi/2), #7
        (   0.0,  phi/2,    0.5), #8
        (   0.0,  phi/2,   -0.5), #9
        (   0.0, -phi/2,   -0.5), #10
        (   0.0, -phi/2,    0.5), #11
    ]
    # 20 equiangular triangles
    faces = [
        [  5,  4, 11,],
        [  5, 11,  1,],
        [  5,  1,  0,],
        [  0,  8,  5,],
        [  5,  8,  4,],
        [  6,  7,  9,],
        [  9,  7,  3,],
        [  3,  7,  2,],
        [  2,  7, 10,],
        [ 10,  7,  6,],
        [  9,  3,  8,],
        [  9,  8,  0,],
        [  9,  0,  6,],
        [  6,  0,  1,],
        [  6,  1, 10,],
        [ 10,  1, 11,],
        [ 10, 11,  2,],
        [  2, 11,  4,],
        [  2,  4,  3,],
        [  3,  4,  8,]
    ]
    return Shape(vertices, faces, colors)
