# ---------------------------------------------------------------------------
# Depth Field
# Mike Christle 2023
# ---------------------------------------------------------------------------
import numpy as np


class Face:
    vertices = []

    def __init__(self, p1, p2, p3):
        self.p1 = p1 - 1
        self.p2 = p2 - 1
        self.p3 = p3 - 1

    def calc_normal(self):
        v1 = Face.vertices[self.p3] - Face.vertices[self.p1]
        v2 = Face.vertices[self.p2] - Face.vertices[self.p1]
        return np.cross(v2, v1)

    def __repr__(self):
        p1 = Face.vertices[self.p1]
        p2 = Face.vertices[self.p2]
        p3 = Face.vertices[self.p3]
        return f'Face({p1}, {p2}, {p3})'
