# graph-anim
This module allows you to create an animation of a graph with a 3D layout rotating in the 3D space about its centroid.
The graph must be specified as an igraph Graph instance. You may specify an igraph Layout instance, or let the module 
compute a 3D 'fr' layout for you. You may optionally specify 'color' and 'size' attributes for the vertex sequence.

The output is a list of .png snapshots of the rotating 3D view at 1 degree intervals. If you have ffmpeg installed, all
snapshots will be compiled into an .mp4 movie as well.
