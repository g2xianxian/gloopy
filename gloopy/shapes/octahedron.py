from .shape import Shape

def Octahedron(radius, face_colors=None):
    vertices = [
        (+radius, 0, 0), # 0
        (0, +radius, 0), # 1
        (0, 0, +radius), # 2
        (0, -radius, 0), # 3
        (0, 0, -radius), # 4
        (-radius, 0, 0), # 5
    ]
    faces = [
        [0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1],
        [5, 2, 1], [5, 3, 2], [5, 4, 3], [5, 1, 4],
    ]
    return Shape(vertices, faces, face_colors)

