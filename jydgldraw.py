# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtOpenGL import *

from OpenGL.GL import *
import OpenGL.arrays.vbo as vbo

import FTGL

import numpy as np
import math

from jydutil import *
from jyddefaultsettings import color_schemes

def make_shader(name):
  print "compiling %s shaders" % (name)
  p = QGLShaderProgram()
  p.addShaderFromSourceFile(QGLShader.Vertex, "shaders/%s.vert" % (name))
  p.addShaderFromSourceFile(QGLShader.Fragment, "shaders/%s.frag" % (name))
  p.link()
  print p.log()
  return p

class GLDraw:

  def __init__(self, font, zoom, colorscheme):

    self.font = font
    self.set_zoom(zoom)
    self.color = colorscheme

    self.circle_shader = make_shader("circle")
    self.circle_move_loc = self.circle_shader.uniformLocation("move")
    self.circle_radius_loc = self.circle_shader.uniformLocation("radius")
    self.circle_inner_loc = self.circle_shader.uniformLocation("inner")
    self.circle_drill_loc = self.circle_shader.uniformLocation("drill")
    self.circle_drill_offset_loc = self.circle_shader.uniformLocation("drill_offset")
    self.rect_shader = make_shader("rect")
    self.rect_size_loc = self.rect_shader.uniformLocation("size")
    self.rect_move_loc = self.rect_shader.uniformLocation("move")
    self.rect_round_loc = self.rect_shader.uniformLocation("round")
    self.rect_drill_loc = self.rect_shader.uniformLocation("drill")
    self.rect_drill_offset_loc = self.rect_shader.uniformLocation("drill_offset")
    self.octagon_shader = make_shader("octagon")
    self.octagon_size_loc = self.octagon_shader.uniformLocation("size")
    self.octagon_move_loc = self.octagon_shader.uniformLocation("move")
    self.octagon_drill_loc = self.octagon_shader.uniformLocation("drill")
    self.octagon_drill_offset_loc = self.octagon_shader.uniformLocation("drill_offset")
    self.hole_shader = make_shader("hole")
    self.hole_move_loc = self.hole_shader.uniformLocation("move")
    self.hole_radius_loc = self.hole_shader.uniformLocation("radius")

    self.square_data = np.array([[-0.5,0.5],[-0.5,-0.5],[0.5,-0.5],[0.5,0.5]], dtype=np.float32)
    self.square_data_vbo = vbo.VBO(self.square_data)

  def set_color(self, t):
    (r,g,b,a) = self.color[t]
    glColor4f(r,g,b,a)

  def set_zoom(self, zoom):
    self.zoom = float(zoom)

  def _txt(self, shape, dx, dy, x, y, on_pad=False):
    if 'name' in shape:
      s = shape['name']
    elif 'value' in shape:
      s = shape['value']
    else: return
    if not on_pad:
      self.set_color(shape['type'])
    else:
      self.set_color('silk')
    l = len(s)
    dxp = dx * self.zoom # dx in pixels
    dyp = dy * self.zoom # dy in pixels
    dxp = dxp / 16. / l # dx in 16 pixel char units
    dyp = dyp / 24. # dy in 24 pixel units
    d = min(dxp, dyp, 100.0)
    f = int(24.*d*1.25)
    self.font.FaceSize(f)
    (slx, sly, slz, srx, sry, srz) = self.font.BBox(s)
    sdx = srx + (8/l) - slx # points
    sdy = sry - sly # points
    sdx = sdx / self.zoom # converted in GL locations
    sdy = sdy / self.zoom # converted in GL locations
    glRasterPos(x - sdx/2, y - sdy/2)
    self.font.Render(s)

  def label(self, shape):
    x = fget(shape,'x')
    y = fget(shape,'y')
    dy = fget(shape,'dy', 1.2)
    dx = fget(shape,'dx', 100.0) # arbitrary large number
    self._txt(shape, dx, dy, x, y)

  def _disc(self, x, y, rx, ry, drill, drill_dx, drill_dy, irx = 0.0, iry = 0.0):
    self.circle_shader.bind()
    self.circle_shader.setUniformValue(self.circle_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.circle_shader.setUniformValue(self.circle_radius_loc, rx, ry)
    self.circle_shader.setUniformValue(self.circle_inner_loc, irx, iry)
    self.circle_shader.setUniformValue(self.circle_drill_loc, drill, 0.0)
    self.circle_shader.setUniformValue(self.circle_drill_offset_loc, drill_dx, drill_dy)
    glDrawArrays(GL_QUADS, 0, 4)
    self.circle_shader.release() 

  def _hole(self, x, y, rx, ry):
    self.set_color('hole')
    self.hole_shader.bind()
    self.hole_shader.setUniformValue(self.hole_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.hole_shader.setUniformValue(self.hole_radius_loc, rx, ry)
    glDrawArrays(GL_QUADS, 0, 4)
    self.hole_shader.release() 

  def disc(self, shape):
    r = fget(shape, 'dx') / 2
    r = fget(shape, 'r', r)
    rx = fget(shape, 'rx', r)
    dy = fget(shape, 'dy') / 2
    if dy > 0:
      ry = fget(shape, 'ry', dy)
    else:
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
      self._txt(shape, rx*2, ry*2, x, y, True)

  def circle(self, shape):
    r = fget(shape, 'dx') / 2
    r = fget(shape, 'r', r)
    rx = fget(shape, 'rx', r)
    dy = fget(shape, 'dy') / 2
    if dy > 0:
      ry = fget(shape, 'ry', dy)
    else:
      ry = fget(shape, 'ry', r)
    x = fget(shape,'x')
    y = fget(shape,'y')
    w = fget(shape,'w')
    irx = fget(shape, 'irx', rx)
    rx = rx + w/2
    irx = irx - w/2
    iry = fget(shape, 'iry', ry)
    ry = ry + w/2
    iry = iry - w/2
    drill = fget(shape,'drill')
    drill_dx = fget(shape,'drill_dx')
    drill_dy = fget(shape,'drill_dy')
 
    self._disc(x, y, rx, ry, drill, drill_dx, drill_dy, irx, iry)
    if drill > 0.0:
      self._hole(x,y, drill/2, drill/2)
    if 'name' in shape:
      self._txt(shape, max(rx*2, drill), max(ry*2, drill), x, y, True)

  def _octagon(self, x, y, dx, dy, drill, drill_dx, drill_dy):
    self.octagon_shader.bind()
    self.octagon_shader.setUniformValue(self.octagon_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.octagon_shader.setUniformValue(self.octagon_size_loc, dx, dy)
    self.octagon_shader.setUniformValue(self.octagon_drill_loc, drill, 0.0)
    self.octagon_shader.setUniformValue(self.octagon_drill_offset_loc, drill_dx, drill_dy)
    glDrawArrays(GL_QUADS, 0, 4)
    self.octagon_shader.release() 

  def octagon(self, shape):
    r = fget(shape, 'r', 0.0)
    dx = fget(shape, 'dx', r*2)
    dy = fget(shape, 'dy', r*2)
    x = fget(shape,'x')
    y = fget(shape,'y')
    drill = fget(shape,'drill')
    drill_dx = fget(shape,'drill_dx')
    drill_dy = fget(shape,'drill_dy')
 
    self._octagon(x, y, dx, dy, drill, drill_dx, drill_dy)
    if drill > 0.0:
      self._hole(x,y, drill/2, drill/2)
    if 'name' in shape:
      self._txt(shape, dx, dy, x, y, True)

  def rect(self, shape):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape, 'dx')
    dy = fget(shape, 'dy')
    ro = fget(shape, 'ro') / 100.0
    rot = fget(shape, 'rot')
    drill = fget(shape, 'drill')
    drill_dx = fget(shape, 'drill_dx')
    drill_dy = fget(shape, 'drill_dy')
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
    self.rect_shader.bind()
    self.rect_shader.setUniformValue(self.rect_size_loc, dx, dy)
    self.rect_shader.setUniformValue(self.rect_move_loc, x, y)
    self.rect_shader.setUniformValue(self.rect_round_loc, ro, 0)
    self.rect_shader.setUniformValue(self.rect_drill_loc, drill, 0)
    self.rect_shader.setUniformValue(self.rect_drill_offset_loc, drill_dx, drill_dy)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    glDrawArrays(GL_QUADS, 0, 4)
    self.rect_shader.release()
    if drill > 0.0:
      self._hole(x,y, drill/2, drill/2)
    if 'name' in shape:
      m = min(dx, dy)
      self._txt(shape ,m, m, x, y, True)

  def line(self, shape):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    if (x1 > x2):
      (x1, x2) = (x2, x1)
      (y1, y2) = (y2, y1)
    w = fget(shape, 'w')
    r = w/2
    dx = abs(x1-x2)
    dy = abs(y1-y2)
    l = math.sqrt(dx*dx + dy*dy)
    s = dy / l
    c = dx / l
    ddy = r * c
    ddx = r * s
    glBegin(GL_QUADS)
    if (y1 > y2):
      ddx = -ddx
      ddy = -ddy
    glVertex3f(x1-ddx, y1+ddy, 0)
    glVertex3f(x1+ddx, y1-ddy, 0)
    glVertex3f(x2+ddx, y2-ddy, 0)
    glVertex3f(x2-ddx, y2+ddy, 0)
    glEnd()
    self._disc(x1, y1, r, r, 0.0, 0.0, 0.0)
    self._disc(x2, y2, r, r, 0.0, 0.0, 0.0)
    
  def draw(self, shapes):
    for shape in shapes:
      self.set_color(shape['type'])
      if 'shape' in shape:
        if shape['shape'] == 'circle': self.circle(shape)
        if shape['shape'] == 'disc': self.disc(shape)
        if shape['shape'] == 'label': self.label(shape)
        if shape['shape'] == 'line': self.line(shape)
        if shape['shape'] == 'octagon': self.octagon(shape)
        if shape['shape'] == 'rect': self.rect(shape)

class JYDGLWidget(QGLWidget):

  def __init__(self, parent):
    super(JYDGLWidget, self).__init__(parent)
    self.parent = parent
    self.colorscheme = color_schemes[str(parent.setting('gl/colorscheme'))]
    start_zoomfactor = int(parent.setting('gl/zoomfactor'))
    self.zoomfactor = start_zoomfactor
    self.zoom_changed = False
    font_file = str(parent.setting('gl/fontfile'))
    self.font = FTGL.PixmapFont(font_file)
    self.shapes = []
    self.make_dot_field()

  def make_dot_field(self):
    gldx = int(self.parent.setting('gl/dx'))
    gldy = int(self.parent.setting('gl/dy'))
    self.dot_field_data = np.array(
      [[x,y] for x in range(-gldx/2, gldx/2) for y in range(-gldy/2, gldy/2)],
      dtype=np.float32)

  def make_dot_field_vbo(self):
    self.dot_field_vbo = vbo.VBO(self.dot_field_data)

  def initializeGL(self):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    #glEnable(GL_POLYGON_STIPPLE)
    #pattern=np.fromfunction(lambda x,y: 0xAA, (32,32), dtype=uint1)
    #glPolygonStipple(pattern)
    (r,g,b,a) = self.colorscheme['background']
    glClearColor(r, g, b, a)
    glClear(GL_COLOR_BUFFER_BIT)
    self.make_dot_field_vbo()
    self.gldraw = GLDraw(self.font, self.zoomfactor, self.colorscheme)

  def paintGL(self):
    new_colorscheme = color_schemes[str(self.parent.setting('gl/colorscheme'))]
    if new_colorscheme != self.colorscheme:
      (r,g,b,a) = new_colorscheme['background']
      glClearColor(r, g, b, a)
      glClear(GL_COLOR_BUFFER_BIT)
    self.colorscheme = new_colorscheme
    self.gldraw.color = self.colorscheme
    if self.zoom_changed:
      self.gldraw.set_zoom(self.zoomfactor)
    glClear(GL_COLOR_BUFFER_BIT)
    (r, g, b, a) = self.colorscheme['grid']
    glColor4f(r, g, b, a)
    self.dot_field_vbo.bind() # make this vbo the active one
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.dot_field_vbo)
    gldx = int(self.parent.setting('gl/dx'))
    gldy = int(self.parent.setting('gl/dy'))
    glDrawArrays(GL_POINTS, 0, gldx * gldy)

    (r, g, b, a) = self.colorscheme['axes']
    glColor4f(r, g, b, a)
    glLineWidth(1)
    glBegin(GL_LINES)
    glVertex3f(-100, 0, 0)
    glVertex3f(100, 0, 0)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0, -100, 0)
    glVertex3f(0, 100, 0)
    glEnd()
        
    if self.shapes != None: self.gldraw.draw(self.shapes)
    if self.zoom_changed:
      self.zoom_changed = False
      self.resizeGL(self.width(), self.height())

  def resizeGL(self, w, h):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # every 'zoomfactor' pixels is one mm
    mm_visible_x = float(w)/self.zoomfactor
    if mm_visible_x < 1: mm_visible_x = 1.0
    mm_visible_y = float(h)/self.zoomfactor
    if mm_visible_y < 1: mm_visible_y = 1.0
    glOrtho(-mm_visible_x/2, mm_visible_x/2, -mm_visible_y/2, mm_visible_y/2, -1, 1)
    glViewport(0, 0, w, h)

  def set_shapes(self, s):
    self.shapes = s
    self.updateGL()

  def wheelEvent(self, event):
    if (event.delta() != 0.0):
      if event.delta() < 0.0:
        if self.zoomfactor > 5:
          self.zoomfactor = self.zoomfactor - 5
          self.parent.zoom_selector.setText(str(self.zoomfactor))
          self.zoom_changed = True
          self.updateGL()
      else:
        if self.zoomfactor < 245:
          self.zoom_changed = True
          self.updateGL()
          self.zoomfactor = self.zoomfactor + 5
          self.parent.zoom_selector.setText(str(self.zoomfactor))
          self.zoom_changed = True
          self.updateGL()
    event.ignore()
