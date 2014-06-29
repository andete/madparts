# (c) 2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from mutil.mutil import *
from defaultsettings import color_schemes

class JYDGVWidget(QtGui.QGraphicsView):

  def __init__(self, parent):
    self.scene = QtGui.QGraphicsScene()
    super(JYDGVWidget, self).__init__(self.scene, parent)
    self.scene.setBackgroundBrush(Qt.black)
    self.scene.addText('Hello, world')
    self.zoomfactor = 42
    self.is_gl = False
    self.color_scheme = color_schemes[str(parent.setting('gl/colorscheme'))]
    self.brush = QtGui.QBrush(Qt.SolidPattern)
    self.no_brush = QtGui.QBrush(Qt.NoBrush)
    self.scale(self.zoomfactor,self.zoomfactor)

  def set_shapes(self, shapes):
    self.shapes = shapes
    self.update()

  def update(self):
    self.draw_shapes()

  def set_color(self, t):
    if t == 'cu':
      t = 'smd'
    (r,g,b,a) = self.color_scheme.get(t, self.color_scheme['unknown'])
    self.color = QtGui.QColor.fromRgbF(r,g,b,a)
    self.brush = QtGui.QBrush(self.color, Qt.SolidPattern)
    self.pen = QtGui.QPen(self.color)

  def skip(self, shape):
    pass

  def circle(self, shape):
    r = fget(shape, 'r')
    rx = fget(shape, 'rx', r)
    ry = fget(shape, 'ry', r)
    x = fget(shape,'x')
    y = fget(shape,'y')
    w = fget(shape,'w')
    # TODO irx/iry handling
    # TODO a1/a2 handling
    self.pen.setWidth(w)
    self.scene.addEllipse(x-rx, y-ry, rx*2, ry*2, self.pen, self.no_brush)

  def disc(self, shape):
    pass

  def label(self, shape):
    pass

  def vertex(self, shape):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    # TODO curves
    self.pen.setWidth(w)
    self.scene.addLine(x1,y1,x2,y2, self.pen)

  def octagon(self, shape):
    pass

  def rect(self, shape):
    pass

  def polygon(self, shape):
    w = fget(shape, 'w')
    vert= shape['v']
    for x in vert:
      x['w'] = w
      self.vertex(x)

  def hole(self, shape):
    pass

  def draw_shapes(self):
    # really ugly redraw everything
    self.scene.clear()
    for shape in self.shapes:
      self.set_color(shape['type'])
      if 'shape' in shape:
        dispatch = {
          'circle': self.circle,
          'disc': self.disc,
          'label': self.label,
          'line': self.vertex,
          'vertex': self.vertex,
          'octagon': self.octagon,
          'rect': self.rect,
          'polygon': self.polygon,
          'hole': self.hole,
        }
        dispatch.get(shape['shape'], self.skip)(shape)
