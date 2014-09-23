# (c) 2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from PySide.QtWebKit import QGraphicsWebView

from mutil.mutil import *
from defaultsettings import color_schemes
import numpy as np
from math import sqrt, pi
import svgfig
import math
import random

def ex1():
  angle_axis = svgfig.LineAxis(5, 0, 5, 2*pi, 0, 2*pi, stroke='white', text_attr={'fill':'white'})
  angle_axis.text_start = -2.5
  angle_axis.text_angle = 180.
  angle_axis.ticks = [x*2*pi/8 for x in range(8)]
  angle_axis.labels = lambda x: "%g" % (x*180/pi)
  angle_axis.miniticks = [x*2*pi/8/9 for x in range(8*9)]

  radial_axis = svgfig.XAxis(0, 5, aty=pi/2, stroke='white', text_attr={'fill':'white'})
  radial_axis.text_start = 5
  radial_axis.text_angle = 90.
  radial_axis.ticks = range(5)

  points = [(max(0.5, random.gauss(2.5, 1)), random.uniform(-pi, pi), max(0.1, random.gauss(0.3, 0.1))) for i in range(10)]
  xerr = svgfig.XErrorBars(points, stroke='white')
  yerr = svgfig.YErrorBars(points, stroke='white')
  dots = svgfig.Dots(points, svgfig.make_symbol("name", stroke="white", fill="red", stroke_width="0.25pt"))
  xml = svgfig.Fig(svgfig.Fig(angle_axis, radial_axis, xerr, yerr, dots, trans="x*cos(y), x*sin(y)")).SVG(svgfig.window(-6, 6, -6, 6)).standalone_xml()
  return QtCore.QByteArray(xml)

class JYDSVGWidget(QtGui.QGraphicsView):

  def __init__(self, parent, box):
    self.scene = QtGui.QGraphicsScene()
    super(JYDSVGWidget, self).__init__(self.scene, parent)
    self.parent = parent
    self.box = box
    self.webview = QGraphicsWebView()
    self.webview.setZoomFactor(0.5)
    self.scene.setBackgroundBrush(Qt.black)
    self.scene.addItem(self.webview)
    #self.scene.addText('Hello, world')
    self.zoomfactor = 42
    self.is_gl = False
    self.color_scheme = color_schemes[str(parent.setting('gl/colorscheme'))]
    self.brush = QtGui.QBrush(Qt.SolidPattern)
    self.no_brush = QtGui.QBrush(Qt.NoBrush)
    self.q = 10
    self.scale(self.zoomfactor/self.q, self.zoomfactor/self.q)

  def _line(self, x1, y1, x2, y2, w):
    return svgfig.Line(x1, y1, x2, y2, stroke_width=w, stroke=self.color).SVG()

  def _ellipse(self, x, y, rx, ry, brush, w=0.001):
    self.pen.setWidth(w*self.q)
    self.scene.addEllipse(x*self.q, -y*self.q, rx*self.q, -ry*self.q, self.pen, brush)

  def draw_dot_field(self):
    self.dot_field_data = np.array(
      [[x,y] for x in range(-self.dx/2, self.dx/2+1) for y in range(-self.dy/2, self.dy/2+1)],
      dtype=np.float32)
    #grid drawing is really slow
    #re-enable when it is not redrawn every time
    self.set_color('grid')
    #for (x,y) in self.dot_field_data:
    #  self.scene.addEllipse(x, y, 0.001, 0.001, self.pen, self.brush)
    r = 0.05
    rpx = "%spx" % (r)
    dots = svgfig.Dots(self.dot_field_data, svgfig.make_symbol("dot_field", stroke=None, fill=self.color, r=r))
    self.set_color('axes')
    l1 = self._line(-self.dx/2,0,self.dx/2,0, r)
    l2 = self._line(0,-self.dy/2, 0, self.dy/2, r)
    return (dots.SVG(), l1, l2)

  def set_shapes(self, shapes):
    self.shapes = shapes
    self.update()

  def update(self):
    self.draw_shapes()

  def set_color(self, t):
    if t == 'cu':
      t = 'smd'
    (r,g,b,a) = self.color_scheme.get(t, self.color_scheme['unknown'])
    self.color = svgfig.rgb(r,g,b)
    self.opacity = a

  # todo use itemgroups?
  def _hole(self, x, y, rx, ry):
    self.set_color('hole')
    self._ellipse(x-rx, y-ry, rx*2, ry*2, self.no_brush)
    rxa = rx/sqrt(2.0)
    rya = ry/sqrt(2.0)
    self._line(x-rxa, y-rya, x+rxa ,y+rya, 0.001)
    self._line(x+rxa, y-rya, x-rxa ,y+rya, 0.001)

  def _disc(self, x, y, rx, ry, drill, drill_dx, drill_dy, irx = 0.0, iry = 0.0):
    self._ellipse(x-rx, y-ry, rx*2, ry*2, self.brush)
    self.color = QtGui.QColor.fromRgbF(0, 0, 0, 1.0)
    self.brush = QtGui.QBrush(self.color, Qt.SolidPattern)
    self._ellipse(x+drill_dx-drill/2, y+drill_dy+-drill/2, drill, drill, self.brush)

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
    drill_dx = fget(shape,'drill_dx')
    drill_dy = fget(shape,'drill_dy')
    self._disc(x, y, rx, ry, drill, drill_dx, drill_dy)
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
    drill_dx = fget(shape, 'drill_dx')
    drill_dy = -fget(shape, 'drill_dy')
    if rot not in [0, 90, 180, 270]:
      raise Exception("only 0, 90, 180, 270 rotation supported for now")
    if rot in [90, 270]:
      (dx, dy) = (dy, dx)
    if rot == 90:
      (drill_dx, drill_dy) = (drill_dy, drill_dx)
    if rot == 180:
      (drill_dx, drill_dy) = (-drill_dx, drill_dy)
    if rot == 270:
      (drill_dx, drill_dy) = (-drill_dy, -drill_dx)
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
    #self.scene.clear()
    #self.webview.load(QtCore.QUrl("/home/joost/prj/madparts/gui/tmp.svg"))
    w = self.width()*.5
    h = self.height()*.5
    width = "%spx" % (w)
    height = "%spx" % (h)
    dx = (int(self.parent.gl_dx + 1)/2)*2
    dy = (int(self.parent.gl_dy + 1)/2)*2
    vx = dx
    dy = dy
    self.dx = dx
    self.dy = dy
    print dx, dy
    # TODO: clever viewbox calculation     
    viewbox = "%d %d %d %d" % (-dx/2, -dy/2, dx, dy)
    rect = svgfig.Rect(-dx/2,-dy/2,dx/2,dy/2, fill='black', stroke=None).SVG()
    (dots, l1, l2) = self.draw_dot_field()
    print self.box.contentsRect()
    print width, height, viewbox
    canvas = svgfig.canvas(rect, dots, l1, l2, width=width, height=height, viewBox=viewbox)
    xml = canvas.standalone_xml()
    print xml
    self.webview.setContent(QtCore.QByteArray(xml))
    #self.webview.setContent(ex1())
    return
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
