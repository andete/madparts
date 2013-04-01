# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtOpenGL import *

from OpenGL.GL import *
import OpenGL.arrays.vbo as vbo

import numpy as np
import math, sys
import os.path, pkg_resources, tempfile

from util.util import *
from defaultsettings import color_schemes
from inter import inter

import glFreeType
import shaders

def make_shader(name):
  print "compiling %s shaders" % (name)
  p = QGLShaderProgram()
  vertex = pkg_resources.resource_string(shaders.__name__, "%s.vert" % (name))
  p.addShaderFromSourceCode(QGLShader.Vertex, vertex)
  fragment = pkg_resources.resource_string(shaders.__name__, "%s.frag" % (name))
  p.addShaderFromSourceCode(QGLShader.Fragment, fragment)
  p.link()
  print p.log()
  return p

class GLDraw:

  def __init__(self, glw, font, colorscheme):
    self.glw = glw
    self.font = font
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
    (r,g,b,a) = self.color.get(t, self.color['unknown'])
    glColor4f(r,g,b,a)

  def zoom(self):
    return float(self.glw.zoomfactor)

  def _txt(self, shape, dx, dy, x, y, on_pad=False):
    if 'name' in shape:
      s = str(shape['name'])
    elif 'value' in shape:
      s = str(shape['value'])
    else: return
    if not on_pad:
      self.set_color(shape['type'])
    else:
      self.set_color('silk')
    l = len(s)
    dxp = dx * self.zoom() # dx in pixels
    dyp = dy * self.zoom() # dy in pixels
    (fdx, fdy) = self.font.ft.getsize(s)
    scale = min(dxp / fdx, dyp / fdy)
    sdx = -scale*fdx/2
    sdy = -scale*fdy/2
    glEnable(GL_TEXTURE_2D) # Enables texture mapping
    glPushMatrix()
    glLoadIdentity()
    self.font.glPrint(x*self.zoom()+sdx, y*self.zoom()+sdy, s, scale)
    glPopMatrix ()
    glDisable(GL_TEXTURE_2D)

  def label(self, shape, labels):
    x = fget(shape,'x')
    y = fget(shape,'y')
    dy = fget(shape,'dy', 1.2)
    dx = fget(shape,'dx', 100.0) # arbitrary large number
    self._txt(shape, dx, dy, x, y)
    return labels

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

  def disc(self, shape, labels):
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
      labels.append(lambda: self._txt(shape, max(rx*2, drill), max(ry*2, drill), x, y, True))
    return labels

  def circle(self, shape, labels):
    r = fget(shape, 'r')
    rx = fget(shape, 'rx', r)
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
    self._disc(x, y, rx, ry, 0.0, 0.0, 0.0, irx, iry)
    if 'name' in shape:
      labels.append(lambda: self._txt(shape, rx*2, ry*2, x, y, True))
    return labels

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

  def octagon(self, shape, labels):
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
      labels.append(lambda: self._txt(shape, dx, dy, x, y, True))
    return labels

  def rect(self, shape, labels):
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
      labels.append(lambda: self._txt(shape ,m, m, x, y, True))
    return labels

  def line(self, shape, labels):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    r = w/2

    dx = x2-x1
    dy = y2-y1
    l = math.sqrt(dx*dx + dy*dy)
    px = dy * r / l # trigoniometrics
    py = dx * r / l # trigoniometrics
    glBegin(GL_QUADS)
    glVertex3f(x1-px, y1+py, 0)
    glVertex3f(x1+px, y1-py, 0)
    glVertex3f(x2+px, y2-py, 0)
    glVertex3f(x2-px, y2+py, 0)
    glEnd()
    self._disc(x1, y1, r, r, 0.0, 0.0, 0.0)
    self._disc(x2, y2, r, r, 0.0, 0.0, 0.0)
    return labels
 
  def skip(self, shape, labels):
    return labels
   
  def draw(self, shapes):
    labels = []
    for shape in shapes:
      self.set_color(shape['type'])
      if 'shape' in shape:
        dispatch = {
          'circle': self.circle,
          'disc': self.disc,
          'label': self.label,
          'line': self.line,
          'octagon': self.octagon,
          'rect': self.rect,
        }
        labels = dispatch.get(shape['shape'], self.skip)(shape, labels)
    for draw_label in labels:
      draw_label()

class JYDGLWidget(QGLWidget):

  def __init__(self, parent):
    super(JYDGLWidget, self).__init__(parent)
    self.parent = parent
    self.colorscheme = color_schemes[str(parent.setting('gl/colorscheme'))]
    start_zoomfactor = int(parent.setting('gl/zoomfactor'))
    self.zoomfactor = start_zoomfactor
    self.zoom_changed = False
    self.auto_zoom = bool(parent.setting('gl/autozoom'))
    # resource_filename does not work in the .zip file py2app makes :(
    # self.font_file = pkg_resources.resource_filename(__name__, "FreeMonoBold.ttf")
    # we work around that by means of a tempfile
    font_data = pkg_resources.resource_string(__name__, 'FreeMonoBold.ttf')
    t = tempfile.NamedTemporaryFile(suffix='.ttf',delete=False)
    t.write(font_data)
    t.close()
    self.font_file = t.name
    self.shapes = []
    self.make_dot_field()
    self.called_by_me = False

  def make_dot_field(self):
    gldx = int(self.parent.setting('gl/dx'))
    gldy = int(self.parent.setting('gl/dy'))
    self.dot_field_data = np.array(
      [[x,y] for x in range(-gldx/2, gldx/2) for y in range(-gldy/2, gldy/2)],
      dtype=np.float32)

  def make_dot_field_vbo(self):
    self.dot_field_vbo = vbo.VBO(self.dot_field_data)

  def initializeGL(self):
    self.glversion = float(glGetString(GL_VERSION).split()[0])
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #glEnable(GL_TEXTURE_2D) # Enables texture mapping
    glEnable(GL_LINE_SMOOTH)
    self.font = glFreeType.font_data(self.font_file, 64)
    #glEnable(GL_POLYGON_STIPPLE)
    #pattern=np.fromfunction(lambda x,y: 0xAA, (32,32), dtype=uint1)
    #glPolygonStipple(pattern)
    (r,g,b,a) = self.colorscheme['background']
    glClearColor(r, g, b, a)
    self.make_dot_field_vbo()
    self.gldraw = GLDraw(self, self.font, self.colorscheme)

  def paintGL(self):
    new_colorscheme = color_schemes[str(self.parent.setting('gl/colorscheme'))]
    if new_colorscheme != self.colorscheme:
      (r,g,b,a) = new_colorscheme['background']
      glClearColor(r, g, b, a)
    self.colorscheme = new_colorscheme
    self.gldraw.color = self.colorscheme

    if self.zoom_changed:
      self.zoom_changed = False
      self.called_by_me = True
      self.resizeGL(self.width(), self.height())
      self.called_by_me = False

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
    if not self.called_by_me:
      self.parent.compile()

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
          self.zoomfactor = self.zoomfactor + 5
          self.parent.zoom_selector.setText(str(self.zoomfactor))
          self.zoom_changed = True
          self.updateGL()
    event.ignore()
