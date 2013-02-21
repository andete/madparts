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

def make_shader(name):
  print "compiling %s shaders" % (name)
  p = QGLShaderProgram()
  p.addShaderFromSourceFile(QGLShader.Vertex, "shaders/%s.vert" % (name))
  p.addShaderFromSourceFile(QGLShader.Fragment, "shaders/%s.frag" % (name))
  p.link()
  print p.log()
  return p


class GLDraw:

  def __init__(self, font, zoom):
    self.color = {}
    self.txt_color = {}
    self.color['silk'] = (1.0, 1.0, 1.0)
    self.txt_color['silk'] = (0.0, 0.0, 0.0)
    self.color['smd'] =  (0.0, 0.0, 1.0)
    self.txt_color['smd'] =  (1.0, 1.0, 1.0)
    self.color['pad'] =  (0.0, 1.0, 0.0)
    self.txt_color['pad'] =  (0.0, 0.0, 0.0)
    self.color['label'] =  (1.0, 1.0, 1.0)
    self.txt_color['label'] =  (1.0, 1.0, 1.0)
    self.color['meta'] =  (1.0, 1.0, 1.0)
    self.txt_color['meta'] =  (1.0, 1.0, 1.0)

    self.font = font
    self.set_zoom(zoom)

    self.circle_shader = make_shader("circle")
    self.circle_move_loc = self.circle_shader.uniformLocation("move")
    self.circle_radius_loc = self.circle_shader.uniformLocation("radiusin")
    self.rect_shader = make_shader("rect")
    self.rect_scale_loc = self.rect_shader.uniformLocation("scale")
    self.rect_move_loc = self.rect_shader.uniformLocation("move")
    self.rect_round_loc = self.rect_shader.uniformLocation("round")

    self.square_data = np.array([[-0.5,0.5],[-0.5,-0.5],[0.5,-0.5],[0.5,0.5]], dtype=np.float32)
    self.square_data_vbo = vbo.VBO(self.square_data)

  def set_zoom(self, zoom):
    self.zoom = float(zoom)

  def _txt(self, shape, dx, dy, x, y):
    if 'name' in shape:
      s = shape['name']
    else:
      s = shape['value']
    (r,g,b) = self.txt_color[shape['type']]
    glColor3f(r,g,b)
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

  def _circle(self, x, y, rx, ry):
    self.circle_shader.bind()
    self.circle_shader.setUniformValue(self.circle_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.circle_shader.setUniformValue(self.circle_radius_loc, rx, ry)
    glDrawArrays(GL_QUADS, 0, 4)
    self.circle_shader.release() 

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
    self._circle(x, y, rx, ry)
    if 'name' in shape:
      self._txt(shape, rx*2, ry*2, x, y)

  def rect(self, shape):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape, 'dx')
    dy = fget(shape, 'dy')
    ro = fget(shape, 'ro') / 100.0
    rot = fget(shape, 'rot')
    if rot not in [0, 90, 180, 270]:
      raise Exception("only 0, 90, 180, 270 rotation supported for now")
    if rot in [90, 270]:
      (dx, dy) = (dy, dx)
    self.rect_shader.bind()
    self.rect_shader.setUniformValue(self.rect_scale_loc, dx, dy)
    self.rect_shader.setUniformValue(self.rect_move_loc, x, y)
    self.rect_shader.setUniformValue(self.rect_round_loc, ro, 0)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    glDrawArrays(GL_QUADS, 0, 4)
    self.rect_shader.release()
    if 'name' in shape:
      self._txt(shape ,dx, dy, x, y)

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
    self._circle(x1, y1, r, r)
    self._circle(x2, y2, r, r)
    
  def draw(self, shapes):
    for shape in shapes:
      (r,g,b) = self.color[shape['type']]
      glColor3f(r,g,b)
      if 'shape' in shape:
        if shape['shape'] == 'rect': self.rect(shape)
        if shape['shape'] == 'circle': self.circle(shape)
        if shape['shape'] == 'line': self.line(shape)
      elif shape['type'] == 'label':
        self.label(shape)

class JYDGLWidget(QGLWidget):
    def __init__(self, gldx, gldy, font_file, start_zoomfactor, parent = None):
        super(JYDGLWidget, self).__init__(parent)
        self.gldx = gldx
        self.gldy = gldy
        self.dot_field_data = np.array(
          [[x,y] for x in range(-gldx/2, gldx/2) for y in range(-gldy/2, gldy/2)],
          dtype=np.float32)
        self.zoomfactor = start_zoomfactor
        self.zoom_changed = False
        self.shapes = []
        self.font = FTGL.PixmapFont(font_file)

    def initializeGL(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.dot_field_vbo = vbo.VBO(self.dot_field_data)
        self.gldraw = GLDraw(self.font, self.zoomfactor)

    def paintGL(self):
        if self.zoom_changed:
          self.gldraw.set_zoom(self.zoomfactor)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(0.5, 0.5, 0.5)
        self.dot_field_vbo.bind() # make this vbo the active one
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.dot_field_vbo)
        glDrawArrays(GL_POINTS, 0, self.gldx*self.gldy)

        glColor3f(1.0, 0.0, 0.0)
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
