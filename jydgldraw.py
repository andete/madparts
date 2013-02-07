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

class GLDraw:

  def __init__(self, font, zoom):
    self.font = font
    self.set_zoom(zoom)

    self.circle_shader = QGLShaderProgram()
    self.circle_shader.addShaderFromSourceFile(QGLShader.Vertex, "shaders/circle.vert")
    self.circle_shader.addShaderFromSourceFile(QGLShader.Fragment, "shaders/circle.frag")
    self.circle_shader.link()
    print self.circle_shader.log()
    self.square_data = np.array([[-0.5,0.5],[-0.5,-0.5],[0.5,-0.5],[0.5,0.5]], dtype=np.float32)
    self.square_data_vbo = vbo.VBO(self.square_data)

  def set_zoom(self, zoom):
    self.font.FaceSize(int(24.*zoom/50.), 72)
    (slx, sly, slz, srx, sry, srz) = self.font.BBox("X")
    sdx = srx - slx # points
    sdy = sry - sly # points
    self.sdx = sdx / float(zoom) # converted in GL locations
    self.sdy = sdy / float(zoom) # converted in GL locations

  def rect(self, shape, num):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape, 'dx')
    dy = fget(shape, 'dy')
    glColor3f(0.0, 0.0, 1.0)
    glRectf(-dx/2 + x, -dy/2 + y, dx/2 + x, dy/2 + y)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(x - self.sdx/2, y - self.sdy/2)
    self.font.Render(str(num))

  def circle(self, shape):
    glColor3f(0.0, 0.0, 1.0)
    num_segments = 42
    r = fget(shape, 'dx')/2
    x = fget(shape,'x')
    y = fget(shape,'y')
    glBegin(GL_TRIANGLE_FAN)
    for i in range(0, num_segments):
        theta = 2.0 * math.pi * float(i) / float(num_segments) # get the current angle 
        dx = r * math.cos(theta) # calculate the x component 
        dy = r * math.sin(theta) # calculate the y component 
        glVertex2f(x + dx, y + dy) # output vertex 
    glEnd()

  def s_circle(self, shape):
    # TODO; use shape
    # TODO: use shader parameters to set radius, ...
    self.circle_shader.bind()
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    glDrawArrays(GL_QUADS, 0, 4)
    self.circle_shader.release()
