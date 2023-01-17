# ---------------------------------------------------------------------------
# Depth Field
# Mike Christle 2023
# ---------------------------------------------------------------------------
import math
import numpy as np

from face import Face
from PIL import Image
from os.path import exists

camera = np.array([])
target = np.array([])
view_width = 0.0
view_height = 0.0
image_width = 0
image_height = 0
offset_x = 0
offset_y = 0
scale_x = 0.0
scale_y = 0.0

faces = []
vertices = []
grid = np.zeros((10, 10))
points = []

max_value = 0.0
min_value = float("inf")
df_image = None


# ---------------------------------------------------------------------------
def run(file_name, cam, tar, view, size):
    """Make a depth field image."""

    global camera, target
    global image_width, image_height, offset_x, offset_y
    global scale_x, scale_y, grid, min_value, max_value

    if not exists(file_name):
        raise Exception(f'File does not exist: {file_name}')

    if view[0] <= 0.0 or view[1] <= 0.0:
        raise Exception('Invalid View')

    if size[0] <= 0 or size[1] <= 0:
        raise Exception('Invalid Size')

    # Save parameters
    camera = np.array(cam)
    target = np.array(tar)
    image_width = size[0]
    image_height = size[1]
    offset_x = image_width // 2
    offset_y = image_height // 2
    scale_x = image_width / view[0]
    scale_y = image_height / view[1]
    grid = np.zeros((image_height, image_width))
    max_value = 0.0
    min_value = float("inf")

    # Make image
    read_file(file_name)
    move_target()
    rotate_vertices()

    remove_backward_faces()
    if len(faces) == 0:
        raise Exception('No faces.')

    project_triangles()
    fill_image()

    # Cleanup
    Face.vertices.clear()
    faces.clear()
    vertices.clear()
    points.clear()


# ---------------------------------------------------------------------------
def read_file(file_name):
    """Read the vertices and triangle faces from the object file."""

    with open(file_name) as in_file:
        for line in in_file:
            parts = line.strip().split(' ')
            if parts[0] == 'v':
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                Face.vertices.append(np.array([x, y, z]))
            if parts[0] == 'f':
                v1 = int(parts[1][:-2])
                v2 = int(parts[2][:-2])
                v3 = int(parts[3][:-2])
                faces.append(Face(v1, v2, v3))


# ---------------------------------------------------------------------------
def move_target():
    """Translate all vertices so the target is at the origin."""

    global target, camera

    # Skip if target is at origin
    if target[0] == 0.0 and target[1] == 0.0 and target[2] == 0.0:
        return

    dx, dy, dz = target[0], target[1], target[2]

    target -= dx, dy, dz
    camera -= dx, dy, dx

    for idx in range(len(Face.vertices)):
        Face.vertices[idx] -= dx, dy, dz


# ---------------------------------------------------------------------------
def rotate_vertices():
    """Rotate all vertices so the line of sight in on the Z axis."""

    global camera

    # Calculate angles to rotate about the Y then X axes
    cx, cy, cz = camera[0], camera[1], camera[2]
    print(cx, cy, cz)
    xz = math.sqrt((cx ** 2) + (cz ** 2))
    if round(cz, 8) == 0.0 or round(xz, 8) == 0.0:
        raise Exception('Camera is too close to objects.')
    angle_y = np.arctan(cx / cz)
    angle_x = -np.arctan(cy / xz)

    # Build the translation matrix
    c, s = np.cos(angle_x), np.sin(angle_x)
    tmx = np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])
    c, s = np.cos(angle_y), np.sin(angle_y)
    tmy = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
    tm = np.matmul(tmy, tmx)

    # Rotate points
    camera = np.matmul(camera, tm)
    for i, vertex in enumerate(Face.vertices):
        Face.vertices[i] = np.matmul(vertex, tm)


# ---------------------------------------------------------------------------
def remove_backward_faces():
    """
    Calculate the normal vector for each triangle face. If the Z
    component of the normal is negative, then the triangle faces
    away from the camera and can be deleted.
    """

    for idx in range(len(faces) - 1, -1, -1):
        face = faces[idx]
        normal = face.calc_normal()
        if normal[2] <= 0.0:
            faces.remove(face)


# ---------------------------------------------------------------------------
def project_triangles():
    """Project each triangle onto the XY plane."""

    for idx in range(len(Face.vertices)):
        point = Face.vertices[idx]
        vertices.append(project_point(point))

    for face in faces:
        p1 = vertices[face.p1]
        p2 = vertices[face.p2]
        p3 = vertices[face.p3]

        fill_line(p1, p2)
        fill_line(p2, p3)
        fill_line(p3, p1)

        points.sort()
        points.sort(key=lambda x: x[1])
        fill_triangle()


# ---------------------------------------------------------------------------
def project_point(point):
    """Project a point onto the XY plane."""

    cz = camera[2]
    dz = cz - point[2]
    if dz <= 0.0:
        raise Exception('Camera is too close.')
    nx = point[0] * cz / dz
    nx = int(nx * scale_x) + offset_x
    ny = point[1] * cz / dz
    ny = image_height - int(ny * scale_y) - offset_y
    ds = np.sqrt(np.sum(np.square(camera - point)))
    return nx, ny, ds


# ---------------------------------------------------------------------------
def fill_triangle():
    """Fill a triangle on the XY plane."""

    if len(points) > 1 and points[0][1] != points[1][1]:
        p1 = points.pop(0)
        fill_point(p1[0], p1[1], p1[2])

    while len(points) > 1:
        p1 = points.pop(0)
        p2 = points.pop(0)
        if p2[0] == p1[0]:
            fill_point(p1[0], p1[1], p1[2])
            continue
        if p1[0] > p2[0]:
            p1, p2 = p2, p1
        x = p1[0]
        y = p1[1]
        v = p1[2]
        dv = (p2[2] - p1[2]) / (p2[0] - p1[0])
        while x <= p2[0]:
            fill_point(x, y, v)
            x += 1
            v += dv


# ---------------------------------------------------------------------------
def fill_line(p1, p2):
    """
    Fill the points list with the points along a line between two points.
    """

    length = p2[1] - p1[1]
    if length == 0:
        return

    if length < 0:
        length = -length
        p1, p2 = p2, p1

    x, y, v = p1[0], p1[1], p1[2]
    delta_x = (p2[0] - p1[0]) / length
    delta_value = (p2[2] - p1[2]) / length
    for _ in range(length):
        points.append((int(x), int(y), v))
        x += delta_x
        y += 1
        v += delta_value


# ---------------------------------------------------------------------------
def fill_point(x, y, value):
    """Fill the grid with the depth values for a point."""

    global min_value, max_value

    if 0 <= x < image_width and 0 <= y < image_height:
        current = grid[y][x]
        if current == 0.0 or current > value:
            grid[y][x] = value
            if value > max_value:
                max_value = value
            if value < min_value:
                min_value = value


# ---------------------------------------------------------------------------
def fill_image():
    """Fill an RGB image with the depth field image."""

    global df_image, min_value

    df_image = Image.new(mode="RGB", size=(image_width, image_height))
    delta_v = (max_value - min_value) / 250.0
    if round(delta_v, 6) == 0.0:
        min_value -= 250.0
        delta_v = 1.0

    for y in range(image_height):
        for x in range(image_width):
            value = grid[y][x]
            if value == 0.0:
                value = int(0)
            else:
                value = 255 - int((value - min_value) / delta_v)
            pixel = value, value, value
            df_image.putpixel((x, y), pixel)

    df_image.show()
