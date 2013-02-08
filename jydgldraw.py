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

    self.square_data = np.array([[-0.5,0.5],[-0.5,-0.5],[0.5,-0.5],[0.5,0.5]], dtype=np.float32)
    self.square_data_vbo = vbo.VBO(self.square_data)

  def set_zoom(self, zoom):
    self.font.FaceSize(int(24.*zoom/50.), 72)
    (slx, sly, slz, srx, sry, srz) = self.font.BBox("X")
    sdx = srx - slx # points
    sdy = sry - sly # points
    self.sdx = sdx / float(zoom) # converted in GL locations
    self.sdy = sdy / float(zoom) # converted in GL locations

  def circle(self, shape, num):
    glColor3f(0.0, 0.0, 1.0)
    # TODO allow better customization of circle
    r = fget(shape, 'dx')/2
    x = fget(shape,'x')
    y = fget(shape,'y')
    self.circle_shader.bind()
    self.circle_shader.setUniformValue(self.circle_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.circle_shader.setUniformValue(self.circle_radius_loc, r, 0)
    glDrawArrays(GL_QUADS, 0, 4)
    self.circle_shader.release()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(x - self.sdx/2, y - self.sdy/2)
    self.font.Render(str(num))
    # TODO, factor out number writing

  def rect(self, shape, num):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape, 'dx')
    dy = fget(shape, 'dy')
    glColor3f(0.0, 0.0, 1.0)
    glRasterPos(x, y)
    self.rect_shader.bind()
    self.rect_shader.setUniformValue(self.rect_scale_loc, dx, dy)
    self.rect_shader.setUniformValue(self.rect_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    glDrawArrays(GL_QUADS, 0, 4)
    self.rect_shader.release()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(x - self.sdx/2, y - self.sdy/2)
    self.font.Render(str(num))

