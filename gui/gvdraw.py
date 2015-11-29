# (c) 2014-2015 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from mutil.mutil import *
from defaultsettings import color_schemes
import numpy as np
from math import sqrt

class JYDGVWidget(QtGui.QGraphicsView):

  def __init__(self, parent):
    self.scene = QtGui.QGraphicsScene()
    super(JYDGVWidget, self).__init__(self.scene, parent)
    self.parent = parent
    self.scene.setBackgroundBrush(Qt.black)
    self.scene.addText('Hello, world')
    self.zoomfactor = 42
    self.is_gl = False
    self.color_scheme = color_schemes[str(parent.setting('gl/colorscheme'))]
    self.brush = QtGui.QBrush(Qt.SolidPattern)
    self.no_brush = QtGui.QBrush(Qt.NoBrush)
    self.make_dot_field()
    self.q = 10
    self.scale(self.zoomfactor/self.q, self.zoomfactor/self.q)

  def make_dot_field(self):
    gldx = int(self.parent.setting('gl/dx'))
    gldy = int(self.parent.setting('gl/dy'))
    self.dot_field_data = np.array(
      [[x,y] for x in range(-gldx/2, gldx/2) for y in range(-gldy/2, gldy/2)],
      dtype=np.float32)

  def _line(self, x1, y1, x2, y2, w):
    self.pen.setWidth(w*self.q)
    self.scene.addLine(x1*self.q, -y1*self.q, x2*self.q, -y2*self.q, self.pen)

  def _ellipse(self, x, y, rx, ry, brush, w=0.001):
    self.pen.setWidth(w*self.q)
    self.scene.addEllipse(x*self.q, -y*self.q, rx*self.q, -ry*self.q, self.pen, brush)

  def draw_dot_field(self):
    #grid drawing is really slow
    #re-enable when it is not redrawn every time
    self.set_color('grid')
    for (x,y) in self.dot_field_data:
      self.scene.addEllipse(x*self.q, y*self.q, 0.005, 0.005, self.pen, self.brush)
    self.set_color('axes')
    self._line(-100,0,100,0, 0.0001)
    self._line(0,-100,0,100, 0.0001)

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

  # todo use itemgroups?
  def _hole(self, x, y, rx, ry):
    self.set_color('hole')
    self._ellipse(x-rx, y-ry, rx*2, ry*2, self.no_brush)
    rxa = rx/sqrt(2.0)
    rya = ry/sqrt(2.0)
    self._line(x-rxa, y-rya, x+rxa ,y+rya, 0.001)
    self._line(x+rxa, y-rya, x-rxa ,y+rya, 0.001)

  def _disc(self, x, y, rx, ry, drill, drill_off_dx, drill_off_dy, irx = 0.0, iry = 0.0):
    self._ellipse(x-rx, y-ry, rx*2, ry*2, self.brush)
    self.color = QtGui.QColor.fromRgbF(0, 0, 0, 1.0)
    self.brush = QtGui.QBrush(self.color, Qt.SolidPattern)
    self._ellipse(x+drill_off_dx-drill/2, y+drill_off_dy+-drill/2, drill, drill, self.brush)

  def _txt(self, s, x, y, dy):
    font = QtGui.QFont("Monospace")
    font.setPointSizeF(dy*self.q)
    font.setStyleHint(QtGui.QFont.TypeWriter)
    font.setWeight(QtGui.QFont.Normal)
    st = self.scene.addSimpleText(str(s), font)
    width = st.sceneBoundingRect().width()
    height = st.sceneBoundingRect().height()
    st.setBrush(self.color)
    st.setPos(x*self.q-width/2,-y*self.q-height/2)

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
    self._ellipse(x-rx, y-ry, rx*2, ry*2, self.no_brush, w)

  def disc(self, shape):
    r = fget(shape, 'r')
    rx = fget(shape, 'rx', r)
    ry = fget(shape, 'ry', r)
    x = fget(shape,'x')
    y = fget(shape,'y')
    drill = fget(shape,'drill')
    drill_off_dx = fget(shape,'drill_off_dx')
    drill_off_dy = fget(shape,'drill_off_dy')
    self._disc(x, y, rx, ry, drill, drill_off_dx, drill_off_dy)
    if drill > 0.0:
      self._hole(x,y, drill/2, drill/2)
    if 'name' in shape:
      self.set_color('name')
      self._txt(shape['name'], x, y, max(ry, drill))

  def label(self, shape):
    x = fget(shape,'x')
    y = fget(shape,'y')
    dy = fget(shape,'dy', 1)
    dx = fget(shape,'dx', 100.0) # arbitrary large number
    if 'name' in shape:
      s = str(shape['name'])
    elif 'value' in shape:
      s = str(shape['value'])
    else: return
    self._txt(s, x, y, dy)

  def vertex(self, shape):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    # TODO curves
    self._line(x1,y1,x2,y2, w)

  def octagon(self, shape):
    pass

  def rect(self, shape):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape, 'dx')
    dy = fget(shape, 'dy')
    ro = fget(shape, 'ro') / 100.0
    rot = fget(shape, 'rot')
    drill = fget(shape, 'drill')
    drill_off_dx = fget(shape, 'drill_off_dx')
    drill_off_dy = -fget(shape, 'drill_off_dy')
    if rot not in [0, 90, 180, 270]:
      raise Exception("only 0, 90, 180, 270 rotation supported for now")
    if rot in [90, 270]:
      (dx, dy) = (dy, dx)
    if rot == 90:
      (drill_off_dx, drill_off_dy) = (drill_off_dy, drill_off_dx)
    if rot == 180:
      (drill_off_dx, drill_off_dy) = (-drill_off_dx, drill_off_dy)
    if rot == 270:
      (drill_off_dx, drill_off_dy) = (-drill_off_dy, -drill_off_dx)
    if drill > 0.0:
      self._hole(x,y, drill/2, drill/2)
    if 'name' in shape:
      m = min(dx, dy)/1.5
      self.set_color('name')
      self._txt(shape['name'], x, y, m)

  def polygon(self, shape):
    w = fget(shape, 'w')
    vert= shape['v']
    for x in vert:
      x['w'] = w
      self.vertex(x)

  def hole(self, shape):
    x = fget(shape,'x')
    y = fget(shape,'y')
    drill = fget(shape,'drill')
    if drill > 0.0:
      self._hole(x,y, drill/2, drill/2)

  def draw_shapes(self):
    # really ugly redraw everything
    self.scene.clear()
    self.draw_dot_field()
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
    # TODO set scene rect
