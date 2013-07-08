# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from ctypes import util

from PySide.QtOpenGL import *

from OpenGL.GL import *
import OpenGL.arrays.vbo as vbo

import numpy as np
import math
import os, os.path

from mutil.mutil import *
from defaultsettings import color_schemes

import glFreeType

def make_shader(name):
  print "compiling %s shaders" % (name)
  p = QGLShaderProgram()
  data_dir = os.environ['DATA_DIR']
  vertex = os.path.join(data_dir, 'shaders', "%s.vert" % (name))
  p.addShaderFromSourceFile(QGLShader.Vertex, vertex)
  fragment = os.path.join(data_dir, 'shaders', "%s.frag" % (name))
  p.addShaderFromSourceFile(QGLShader.Fragment, fragment)
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
    self.circle_angles_loc = self.circle_shader.uniformLocation("angles")

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
    if (len(s) == 0):
      return # Do nothing if there's no text
    dxp = dx * self.zoom() # dx in pixels
    dyp = dy * self.zoom() # dy in pixels
    (fdx, fdy) = self.font.ft.getsize(s)
    scale = 1.6*min(dxp / fdx, dyp / fdy)
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
    dy = fget(shape,'dy', 1)
    dx = fget(shape,'dx', 100.0) # arbitrary large number
    self._txt(shape, dx, dy, x, y)
    return labels

  def _disc(self, x, y, rx, ry, drill, drill_dx, drill_dy, irx = 0.0, iry = 0.0, a1 = 0.0, a2 = 360.0):
    self.circle_shader.bind()
    self.circle_shader.setUniformValue(self.circle_move_loc, x, y)
    self.square_data_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, self.square_data_vbo)
    self.circle_shader.setUniformValue(self.circle_radius_loc, rx, ry)
    self.circle_shader.setUniformValue(self.circle_inner_loc, irx, iry)
    self.circle_shader.setUniformValue(self.circle_drill_loc, drill, 0.0)
    self.circle_shader.setUniformValue(self.circle_drill_offset_loc, drill_dx, drill_dy)
    a1 = (a1 % 361) * math.pi / 180.0
    a2 = (a2 % 361) * math.pi / 180.0
    self.circle_shader.setUniformValue(self.circle_angles_loc, a1, a2)
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
      labels.append(lambda: self._txt(shape, max(rx*1.5, drill), max(ry*1.5, drill), x, y, True))
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
    a1 = fget(shape, 'a1', 0.0)
    a2 = fget(shape, 'a2', 360.0)
    self._disc(x, y, rx, ry, 0.0, 0.0, 0.0, irx, iry, a1, a2)
    if 'name' in shape:
      labels.append(lambda: self._txt(shape, rx*1.5, ry*1.5, x, y, True))
    if abs(a1 - a2) > 0.25:
      x1 = r * math.cos(a1*math.pi/180)
      y1 = r * math.sin(a1*math.pi/180)
      x2 = r * math.cos(a2*math.pi/180)
      y2 = r * math.sin(a2*math.pi/180)
      self._disc(x1, y1, w/2, w/2, 0.0, 0.0, 0.0)
      self._disc(x2, y2, w/2, w/2, 0.0, 0.0, 0.0)
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
      labels.append(lambda: self._txt(shape, dx/1.5, dy/1.5, x, y, True))
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
      m = min(dx, dy)/1.5
      labels.append(lambda: self._txt(shape ,m, m, x, y, True))
    return labels

  def vertex(self, shape, labels):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    curve = fget(shape, 'curve', 0.0)
    angle = curve*math.pi/180.0
    r = w/2

    dx = x2-x1
    dy = y2-y1
    l = math.sqrt(dx*dx + dy*dy)
    if angle == 0.0:
      px = dy * r / l # trigoniometrics
      py = dx * r / l # trigoniometrics
      glBegin(GL_QUADS)
      glVertex3f(x1-px, y1+py, 0)
      glVertex3f(x1+px, y1-py, 0)
      glVertex3f(x2+px, y2-py, 0)
      glVertex3f(x2-px, y2+py, 0)
      glEnd()
    else:
      print "x1:",x1,"y1:",y1
      print "x2:",x2,"y2:",y2
      dx = x2-x1
      dy = y2-y1
      print "dx:",dx, "dy:", dy, "l:", l
      # radius of arc
      # this will only work for arcs
      # up to 180 degrees!
      # sin(angle/2) = (l/2) / rc =>
      angle_for_sin = abs(angle)
      if angle_for_sin > math.pi:
        angle_for_sin = -(2*math.pi-angle)
      rc = l / (2 * math.sin(angle_for_sin/2))
      print "rc:", rc
      # a = sqrt(rc^2 - (l/2)^2) 
      a = math.sqrt((rc * rc) - (l*l/4))
      print "a:", a
      # unit vector pointing from (x1,y1) to (x2,y2)
      (ndx, ndy) = (dx / l, dy / l)
      print "ndx:",ndx,"ndy:",ndy
      # perpendicular unit vector
      (pdx, pdy) = (-ndy, ndx)
      print "pdx:",pdx,"pdy:",pdy
      # center point of arc 
      # point in between (x1,y1) and (x2,y2) shifted negatively among (pdx,pdy)
      (x3,y3) = ((x1+x2)/2, (y1+y2)/2) 
      print "x3:",x3,"y3:",y3
      fx = a*pdx
      fy = a*pdy
      if rc > 0:
        fx = -fx
        fy = -fy
      if angle > 0:
        fx = -fx
        fy = -fy
      x0 = x3 + fx
      y0 = y3 + fy
      print "x0:",x0,"y0:",y0
      (d1,d2) = (y1-y0, y2-y0)
      (e1,e2) = (x1-x0, x2-x0)
      print "d1:",d1,"d2:",d2
      print "e1:",e1,"e2:",e2
      a1s = math.asin(d1/rc)
      a1 = math.acos(e1/rc)
      a2s = math.asin(d2/rc)
      a2 = math.acos(e2/rc)
      if a1s < 0:
        a1 = 2*math.pi - a1
      if a2s < 0:
        a2 = 2*math.pi - a2
      a1 = a1 * 180 / math.pi
      a2 = a2 * 180 / math.pi
      if angle < 0:
        (a1, a2) = (a2, a1)
      print "a1:",a1,"a2:",a2,"curve:",curve
      self._disc(x0, y0, rc+r, rc+r, 0.0, 0.0, 0.0, rc-r, rc-r, a1, a2)
    self._disc(x1, y1, r, r, 0.0, 0.0, 0.0)
    self._disc(x2, y2, r, r, 0.0, 0.0, 0.0)
    return labels
 
  def polygon(self, shape, labels):
    w = fget(shape, 'w')
    vert= shape['v']
    for x in vert:
      x['w'] = w
      labels = self.vertex(x, labels)
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
          'line': self.vertex,
          'vertex': self.vertex,
          'octagon': self.octagon,
          'rect': self.rect,
          'polygon': self.polygon,
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
    data_dir = os.environ['DATA_DIR']
    self.font_file = os.path.join(data_dir, 'gui', 'FreeMonoBold.ttf')
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
    self.glversion = glGetString(GL_VERSION)
    self.glversion = self.glversion.split()[0] # take numeric part
    self.glversion = self.glversion.split('.') # split on dots
    if len(self.glversion) < 2:
      raise Exception("Error parsing openGL version")
    self.glversion = float("%s.%s" % (self.glversion[0], self.glversion[1]))
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
    self.update()

  def wheelEvent(self, event):
    if (event.delta() != 0.0):
      if event.delta() < 0.0:
        if self.zoomfactor > 5:
          self.zoomfactor = self.zoomfactor - 5
          self.parent.zoom_selector.setText(str(self.zoomfactor))
          self.zoom_changed = True
          self.update()
      else:
        if self.zoomfactor < 245:
          self.zoomfactor = self.zoomfactor + 5
          self.parent.zoom_selector.setText(str(self.zoomfactor))
          self.zoom_changed = True
          self.update()
    event.ignore()
