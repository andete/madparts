#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtOpenGL import *

from OpenGL.GL import *
import OpenGL.arrays.vbo as vbo

import numpy as np
import math

def oget(m, k, d):
  if k in m: return m[k]
  return d

def fget(m, k, d = 0.0):
  return float(oget(m, k, d))

def make_shader(name):
  print "compiling %s... shaders" % (name)
  p = QGLShaderProgram()
  p.addShaderFromSourceFile(QGLShader.Vertex, "shaders/%s.vert" % (name))
  p.addShaderFromSourceFile(QGLShader.Fragment, "shaders/%s.frag" % (name))
  p.link()
  print p.log()
  return p

class GLDraw:

  def __init__(self, font, zoom):
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
    self.zoom = zoom
    self.font.FaceSize(int(24.*zoom/50.), 72)
    (slx, sly, slz, srx, sry, srz) = self.font.BBox("X")
    sdx = srx - slx # points
    sdy = sry - sly # points
    self.sdx = sdx / float(zoom) # converted in GL locations
    self.sdy = sdy / float(zoom) # converted in GL locations

  def _circle(self, x, y, rx, ry):
    self.circle_shader.bind()
    self.circle_shader.setUniformValue(self.circle_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.circle_shader.setUniformValue(self.circle_radius_loc, rx, ry)
    glDrawArrays(GL_QUADS, 0, 4)
    self.circle_shader.release() 

  def circle(self, shape, num):
    glColor3f(0.0, 0.0, 1.0)
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
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(x - self.sdx/2, y - self.sdy/2)
    self.font.Render(str(num))
    # TODO, factor out number writing

  def rect(self, shape, num):
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
    glColor3f(0.0, 0.0, 1.0)
    self.rect_shader.bind()
    self.rect_shader.setUniformValue(self.rect_scale_loc, dx, dy)
    self.rect_shader.setUniformValue(self.rect_move_loc, x, y)
    self.rect_shader.setUniformValue(self.rect_round_loc, ro, 0)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    glDrawArrays(GL_QUADS, 0, 4)
    self.rect_shader.release()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(x - self.sdx/2, y - self.sdy/2)
    self.font.Render(str(num))

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
    glColor3f(1.0, 1.0, 1.0)
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
    
