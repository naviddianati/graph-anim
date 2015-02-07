import numpy.random as rd
from mypalettes import mplPalette
import numpy as np
import igraph as ig
import os


def animate(g, layout = None, filename = "frame" , height = 800, rendermovie = True, outfile = 'anim'):
    """
    Rotate 3d layout of graph g and export a .png snapshot 
    for each angle.
    If found, the graphs vertex attributes 'size' and 'color'
    will be use. 'color' should be an RGB  tuple.
    If layout is None, a 3d FR layout will be computed.

    @param g: igraph Graph.
    @param layout: 3d igraph Layout.
    @param filename: filename prefix for .png snapshots.
    @param height: height of output .png files in pixels.
    @param rendermovie: whether or not to render a movie from the snapshots. Requires ffmpeg.
    @param outfile: filename for output movie.
    """

    if 'size' not in g.vs.attribute_names():
        g.vs['size'] = g.degree() 
    
        
    if 'color' not in g.vs.attribute_names():
        g.vs['color'] = [(255,255,255)] * g.vcount()
    
    print "Framing the layout..."
    gg = frame_the_graph(g)

    if layout is None:
        print "computing 3d layout..."
        layout = g.layout_fruchterman_reingold_3d()


    #center the layout
    layout.center(layout.centroid()) 

    y_max = max([item[1] for item in layout.coords])
    x_max = max([item[0] for item in layout.coords])
    y_min = min([item[1] for item in layout.coords])
    x_min = min([item[0] for item in layout.coords])
    k = 1.5

    x_width = max([np.sqrt(point[0] ** 2 + point[2] ** 2) for point in layout.coords])    
    aspect = k*(x_max-x_min) / (y_max-y_min)

    fixed_coords = [[x_width*k,y_max],[x_width*k,y_min],[-x_width*k,y_min],[-x_width*k,y_max]]

    for i in range(360):
        rootpoint = layout.coords[0]
        rootpoint = (0,0,-10)
        layout.rotate(1, 0, 2, origin=rootpoint)
        coords2d = [point[:2] for point in layout.coords]
        
        new_layout = ig.Layout( coords2d +  fixed_coords)
        update_depths(gg,layout)
        
        ig.plot(gg,
            filename + '-%s.png' % str(i).zfill(3),
            vertex_color = gg.vs['color-2'],
            vertex_size = gg.vs['size'],
            vertex_frame_color = gg.vs['color-1'],
            layout = new_layout,
            edge_color = gg.es['color-1'],
            background='black',
            bbox=(0,0,int(aspect*height),height)
           )
    if rendermovie:
        result = os.system(' ffmpeg -y -r 60 -qscale 2 -i %s-%%03d.png %s.mp4' % (filename,outfile))
        if result != 0:
            print "Eerror: could not render movie with ffmpeg."
    






def frame_the_graph(g):
    """
    Add 4 dummy nodes to the graph to fix the view frame.
    
    @return: augmneted graph.
    """
    gg = g.copy()
    gg.add_vertices(4)
    gg.vs[-5:]['gen']= [None] * 4
    v1,v2,v3,v4 =  gg.vs.indices[-4:]
    gg.vs[-4:]['dummy'] = True
    gg.vs[-4:]['color'] = [(0,0,0)] * 4
    #gg.add_edges(((v1,v2),(v2,v3),(v3,v4),(v4,v1)))
    
    return gg




def update_depths(g,layout):
    """
    After rotating the 3d layout, update the vertex and edge
    colors according to the the new depths (z coordinates).

    @param g: igrpah Graph.
    @param layout: igraph 3d layout.
    """
    zs = np.array(layout.coords + [[0,0,0]] * 4)[:,2]
    zs += abs(min(zs))
    zs /= max(zs)

    g.vs['color-1'] = [rgba_to_color_name(list(v['color'])+[zs[i] ** 2]) if v['color'] else 'red' for i,v in enumerate(g.vs)]
    g.vs['color-2'] = [rgba_to_color_name(list(v['color'])+[zs[i]**2*2]) if v['color'] else 'red' for i,v in enumerate(g.vs)]
    g.es['color-1'] = [(0,0,0) if g.vs[e.source]['dummy'] else g.vs[e.source]['color-1'] for e in g.es]
    g.es['color-2'] = [(0,0,0) if g.vs[e.source]['dummy'] else g.vs[e.source]['color-2'] for e in g.es]


def rgba_to_color_name(rgba):
    '''
    @param rgba: a 4-tuple of float values in [0,1]
    @return: a string such as "rgba(100,20,220,0.3)"
    '''
    return "rgba(" + ",".join([str(int(255 * rgba[0])), str(int(255 * rgba[1])), str(int(255 * rgba[2])), '%0.2f' % rgba[3]]) + ")"






if __name__ == "__main__":
    g = ig.Graph.Barabasi(400,1)
    pal = mplPalette(max(g.degree()) + 1,'autumn')

    g.vs['color'] = [pal.get(d) for d in g.degree() ]
    animate(g, filename = 'frame')
