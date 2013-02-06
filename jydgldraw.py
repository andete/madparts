#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from OpenGL.GL import *

import math

def oget(m, k, d):
  if k in m: return m[k]
  return d

def fget(m, k, d = 0.0):
  return float(oget(m, k, d))

class GLDraw:

  def __init__(self, font):
    self.font = font

  def rect(self, shape, num = 1):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape,'dx')
    dy = fget(shape,'dy')
    glColor3f(0.0, 0.0, 1.0)
    glRectf(-dx/2 + x, -dy/2 + y, dx/2 + x, dy/2 + y)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(x-dx/4, y-dy/8)
    #self.font.FaceSize(24, 72)
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
