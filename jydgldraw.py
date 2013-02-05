#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from OpenGL.GL import *

import math

def oget(m, k, d):
  if k in m: return m[k]
  return d

class GLDraw:

  def __init__(self, font):
    self.font = font

  def rect(self, shape, num = 1):
    x = float(shape['x'])
    y = float(shape['y'])
    dx = oget(shape,'dx',0)
    dy = oget(shape,'dy',0)
    glColor3f(0.0, 0.0, 1.0)
    glRectf(-x/2 + dx, -y/2 + dy, x/2 + dx, y/2 + dy)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos(dx-x/4, dy-y/8)
    #self.font.FaceSize(24, 72)
    self.font.Render(str(num))

  def circle(self, shape):
    glColor3f(0.0, 0.0, 1.0)
    num_segments = 42
    r = float(shape['x'])/2
    dx = oget(shape,'dx',0)
    dy = oget(shape,'dy',0)
    glBegin(GL_TRIANGLE_FAN)
    for i in range(0, num_segments):
        theta = 2.0 * math.pi * float(i) / float(num_segments) # get the current angle 
        x = r * math.cos(theta) # calculate the x component 
        y = r * math.sin(theta) # calculate the y component 
        glVertex2f(x + dx, y + dy) # output vertex 
    glEnd()
