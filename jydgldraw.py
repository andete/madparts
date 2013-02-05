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

  def rect(self, shape):
    x = float(shape['x'])
    y = float(shape['y'])
    dx = oget(shape,'dx',0)
    dy = oget(shape,'dy',0)
    glRectf(-x/2 + dx, -y/2 + dy, x/2 + dx, y/2 + dy)    

  def circle(self, shape):
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
