# Depth Field Maker
I recently got interested in making stereogram images.
The first step is to build a 3D model of the objects in the picture.
The next step is to create a depth field image of the hidden objects.
A depth field image is a gray scale image where the gray level corresponds
to the distance from the camera to the object in the picture.

### Making Object Model Files
To build the 3D model I use Wings 3D.
After building the model I export the model to a Wavefront .obj file.
Select the triangulation option, turn off all other options.
All I need is the coordinates of the vertices and the indices of the vertices for each triangle.
If you us some other export format, you need to update the routine 'read_file'.

### Installation
Copy all the files to a folder.

Type: python depth_field.py
 