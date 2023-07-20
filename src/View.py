from matplotlib import pyplot
from mpl_toolkits.mplot3d import art3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import (List)
from latticegeometrylib.Miscellaneous import Size, Periodicity
from ctypes import windll
import cadquery as cq
from latticegeometrylib.CellConfiguration import CellConfiguration


class CellViewer(FigureCanvasTkAgg):
    def __init__(self, widget, width, height):
        self.dpi = get_ppi()
        self.figure, self.axes = pyplot.subplots(nrows=2, ncols=1, figsize=(width / self.dpi, height / self.dpi),
                                                 dpi=self.dpi, subplot_kw={'projection': '3d'},
                                                 gridspec_kw={'height_ratios': [3, 1]})
        FigureCanvasTkAgg.__init__(self, master=widget,figure=self.figure)
        self.axes[0].set_axis_off()
        self.axes[1].set_axis_off()
        self.axes[0].set_box_aspect(aspect=(1, 1, 1))
        self.axes[1].set_box_aspect(aspect=(1, 1, 1))
        self.axes[0].shareview(self.axes[1])

        self.initial_points: List[List[float]] = [[],[],[]]
        self.num_initial_points = 0
        self.points: List[List[float]] = [[],[],[]]
        self.edges: List = []
        self.faces: List = []
        self.dim_logger = []
        self.draw()

    def add_initial_points(self, corner_points: dict | list ):
        self.axes[0].clear()
        self.axes[0].set_axis_off()
        self.axes[0].set_box_aspect(aspect=(1, 1, 1))

        x, y, z = ([],[],[])

        if type( corner_points ) is dict:
            x = [ point.x for point in corner_points.values() ]
            y = [ point.y for point in corner_points.values() ]
            z = [ point.z for point in corner_points.values() ]
        else:
            x = corner_points[ 0 ]
            y = corner_points[ 1 ]
            z = corner_points[ 2 ]

        self.initial_points = [x, y, z]
        self.num_initial_points = len( x )
        self.axes[0].scatter( x, y, z, facecolor='black', s=10 )
        max_value = max(x + y + z)
        self.axes[0].set_xlim( xmin= -max_value * 1.5, xmax=max_value * 1.5)
        self.axes[0].set_ylim( ymin= -max_value * 1.5, ymax=max_value * 1.5)
        self.axes[0].set_zlim( zmin= -max_value * 1.5, zmax=max_value * 1.5)
        for i in range( self.num_initial_points ):
            self.axes[0].text( 1.2 * x[ i ], 1.2 * y[ i ], 1.2 * z[ i ], str( i + 1 ), ma='center')

        self.axes[1].add_line(art3d.Line3D(xs=(0,1),ys=(0.,0.),zs=(0.,0.), color='red'))
        self.axes[1].add_line(art3d.Line3D(xs=(0,0),ys=(0.,1.),zs=(0.,0.), color='green'))
        self.axes[1].add_line(art3d.Line3D(xs=(0,0),ys=(0.,0.),zs=(0.,1.), color='blue'))
        self.axes[1].set_xlim(xmax=1., xmin=-1.)
        self.axes[1].set_ylim(ymax=1., ymin=-1.)
        self.axes[1].set_zlim(zmax=1., zmin=-1.)
        self.axes[1].text(x=1.2, y=0, z=0, s='x', ma='center',color='red')
        self.axes[1].text(x=0, y=1.2, z=0, s='y', ma='center',color='green')
        self.axes[1].text(x=0, y=0, z=1.2, s='z', ma='center',color='blue')
        self.axes[1].set_box_aspect(aspect=(1, 1, 1))

        self.figure.canvas.draw()

    def delete_initial_points(self):
        self.axes[0].clear()
        self.num_initial_points = 0
        for i in self.initial_points: i.clear()
        for l in self.points: l.clear()
        self.edges.clear()
        self.faces.clear()

    def add_point(self, point: cq.Vector):
        self.points[0].append( point.x )
        self.points[1].append( point.y )
        self.points[2].append( point.z )
        self.axes[0].scatter( [point.x], [point.y], [point.z], facecolor='black', s=60)
        self.figure.canvas.draw()
        self.dim_logger.append(0)

    def add_edge(self, p0: cq.Vector, p1: cq.Vector):
        edge = art3d.Line3D( xs = ( p0.x, p1.x ),
                             ys = ( p0.y, p1.y ),
                             zs = ( p0.z, p1.z ),
                             color='black',
                             linewidth=3.0,
                             solid_capstyle='round')
        self.edges.append(edge)
        self.axes[0].add_line(edge)
        self.figure.canvas.draw()
        self.dim_logger.append(1)

    def add_face(self, p0: cq.Vector, p1: cq.Vector, p2: cq.Vector):
        points = [ [p0.toTuple(), p1.toTuple(), p2.toTuple()] ]
        face = art3d.Poly3DCollection(points,facecolor='#B84245', edgecolor='black', linewidth=1.0, alpha=0.6)
        self.faces.append(face)
        self.axes[0].add_collection3d(face)
        self.figure.canvas.draw()
        self.dim_logger.append(2)

    def add_feature(self, features: CellConfiguration ):

        for item in features:
            dim = item.dimension()
            if dim == 0:
                self.add_point( item.geometry[0] )
            elif dim == 1:
                self.add_edge( item.geometry[0], item.geometry[1])
            elif dim == 2:
                self.add_face(item.geometry[0], item.geometry[1],item.geometry[2])

    def pop_point(self):
        if len(self.points[0]) > 0:
            for l in self.points: l.pop()
            self.axes[0].scatter(self.points[0], self.points[1], self.points[2], facecolor='black', s=40)
            self.dim_logger.pop()
            self.figure.canvas.draw()

    def pop_edge(self):
        if len(self.edges) > 0:
            self.edges.pop()
            self.axes[0].lines.pop()
            self.figure.canvas.draw()
            self.dim_logger.pop()

    def pop_face(self):
        if len(self.faces) > 0:
            self.faces.pop()
            self.axes[0].collections.pop()
            self.figure.canvas.draw()
            self.dim_logger.pop()

    def pop_feature(self):
        dim = self.dim_logger[-1]

        if dim == 0:
            self.pop_point()
        elif dim == 1:
            self.pop_edge()
        elif dim == 2:
            self.pop_face()

    def reset(self):
        self.points = [[],[],[]]
        self.edges.clear()
        self.faces.clear()
        self.dim_logger.clear()
        self.axes[0].clear()
        self.axes[0].set_axis_off()
        self.axes[0].set_box_aspect(aspect=(1, 1, 1))
        self.add_initial_points( self.initial_points )
        self.figure.canvas.draw()


class LatticeViewer(FigureCanvasTkAgg):
    def __init__(self, widget, width, height):
        self.dpi = get_ppi()

        self.figure, self.axes = pyplot.subplots( nrows=1, ncols=2, figsize=(width/self.dpi, height/self.dpi),
                                     dpi=self.dpi, subplot_kw={'projection':'3d'}, gridspec_kw={'width_ratios':[3,1]})

        FigureCanvasTkAgg.__init__(self, master=widget,figure=self.figure)

        self.figure.subplots_adjust(left=0,right=1,top=1,bottom=0)
        self.axes[0].set_axis_off()
        self.axes[1].set_axis_off()
        self.axes[0].set_box_aspect(aspect=(1, 1, 1))
        self.axes[1].set_box_aspect(aspect=(1, 1, 1))
        self.axes[0].shareview(self.axes[1])
        self.lengths: Size = Size()
        self.pattern: Periodicity = Periodicity()
        self.draw()

    def create( self, cell_size: Size, pattern: Periodicity ) -> None:
        self.lengths = cell_size
        self.pattern = pattern

        pointsX = [ nx * self.lengths.dx - (1./2.) * self.pattern.nx * self.lengths.dx for nx in range( self.pattern.nx +1) ]
        pointsY = [ ny * self.lengths.dy - (1./2.) * self.pattern.ny * self.lengths.dy for ny in range( self.pattern.ny +1) ]
        pointsZ = [ nz * self.lengths.dz - (1./2.) * self.pattern.nz * self.lengths.dz for nz in range( self.pattern.nz +1) ]

        for x in pointsX:
            for y in pointsY:
                z = self.lengths.dz * self.pattern.nz
                line = art3d.Line3D(xs=(x, x),
                                    ys=(y, y),
                                    zs=(-z/2, z/2),
                                    color='black',
                                    linewidth=1.0,
                                    solid_capstyle='round')
                self.axes[0].add_line(line)

        for x in pointsX:
            for z in pointsZ:
                y = self.lengths.dy * self.pattern.ny
                line = art3d.Line3D(xs=(x, x),
                                    ys=(-y/2, y/2),
                                    zs=(z, z),
                                    color='black',
                                    linewidth=1.0,
                                    solid_capstyle='round')
                self.axes[0].add_line(line)

        for y in pointsY:
            for z in pointsZ:
                x = self.lengths.dx * self.pattern.nx
                line = art3d.Line3D(xs=(-x/2, x/2),
                                    ys=(y, y),
                                    zs=(z, z),
                                    color='black',
                                    linewidth=1.0,
                                    solid_capstyle='round')
                self.axes[0].add_line(line)

        max_comp: int = int( max(
            self.lengths.dx * self.pattern.nx, self.lengths.dy * self.pattern.ny, self.lengths.dz * self.pattern.nz ) )

        self.axes[0].set_xlim( xmax= max_comp * 0.5, xmin=-max_comp* 0.5 )
        self.axes[0].set_ylim( ymax= max_comp* 0.5, ymin=-max_comp* 0.5 )
        self.axes[0].set_zlim( zmax= max_comp* 0.5, zmin=-max_comp* 0.5 )
        self.axes[0].set_box_aspect(aspect=(1, 1, 1))

        self.axes[1].add_line(art3d.Line3D(xs=(0,1),ys=(0.,0.),zs=(0.,0.), color='red'))
        self.axes[1].add_line(art3d.Line3D(xs=(0,0),ys=(0.,1.),zs=(0.,0.), color='green'))
        self.axes[1].add_line(art3d.Line3D(xs=(0,0),ys=(0.,0.),zs=(0.,1.), color='blue'))
        self.axes[1].set_xlim(xmax=1., xmin=-1.)
        self.axes[1].set_ylim(ymax=1., ymin=-1.)
        self.axes[1].set_zlim(zmax=1., zmin=-1.)
        self.axes[1].text(x=1.2, y=0, z=0, s='x', ma='center',color='red')
        self.axes[1].text(x=0, y=1.2, z=0, s='y', ma='center',color='green')
        self.axes[1].text(x=0, y=0, z=1.2, s='z', ma='center',color='blue')
        self.axes[1].set_box_aspect(aspect=(1, 1, 1))

        self.figure.canvas.draw()

    def reset(self) -> None:
        self.axes[0].clear()
        self.axes[0].set_box_aspect(aspect=(1, 1, 1))
        self.axes[0].set_axis_off()

def get_ppi():
    return windll.user32.GetDpiForSystem()
