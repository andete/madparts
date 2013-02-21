# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import StringIO

from xml.sax.saxutils import escape

from bs4 import BeautifulSoup, Tag

from jydutil import *

# this can still use plenty of abstraction
class Export:

  def rect(self, soup, package, shape):
    smd = soup.new_tag('smd')
    smd['name'] = shape['name']
    smd['x'] = fget(shape, 'x')
    smd['y'] = fget(shape, 'y')
    smd['dx'] = fget(shape, 'dx')
    smd['dy'] = fget(shape, 'dy')
    smd['roundness'] = iget(shape, 'ro')
    smd['rot'] = "R%d" % (fget(shape, 'rot'))
    smd['layer'] = 1
    package.append(smd)

  def label(self, soup, package, shape):
    label = soup.new_tag('text')
    x = fget(shape,'x')
    y = fget(shape,'y')
    dy = fget(shape,'dy', 1)
    s = shape['value']
    layer = 21
    if s == "NAME": 
      s = ">NAME"
      layer = 25
    if s == "VALUE": 
      s = ">VALUE"
      layer = 27
    label['x'] = x - len(s)*dy/2
    label['y'] = y - dy/2
    label['size'] = dy
    label['layer'] = layer
    label.string = s
    package.append(label)
  
  def circle(self, soup, package, shape):
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
    w = 0.25
    circle = soup.new_tag('circle')
    circle['x'] = x
    circle['y'] = y
    circle['radius'] = (r-w/2)
    circle['width'] = w
    circle['layer'] = 21
    package.append(circle)

  def line(self, soup, package, shape):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    line = soup.new_tag('wire')
    line['x1'] = x1
    line['y1'] = y1
    line['x2'] = x2
    line['y2'] = y2
    line['width'] = w
    line['layer'] = 21
    package.append(line)

  def load(self, fn):
    with open(fn) as f:
      return BeautifulSoup(f, "xml")
  
  def save(self, fn, soup):
    with open(fn, 'w+') as f:
      f.write(str(soup))
    
  def generate(self, soup, shapes, package):
    # get all meta from shapes:
    for shape in shapes:
      if shape['type'] == 'meta':
        name = eget(shape, 'name', 'Name not found')
        idx = eget(shape, 'id', 'Id not found')
        desc = oget(shape, 'desc', '')
        parent_idx = oget(shape, 'parent', None)
        break
    description = soup.new_tag('description')
    package.append(description)
    parent_str = ""
    if parent_idx != None:
      parent_str = " parent: %s" % parent_idx
    description.string = desc + "\n<br/><br/>\nGenerated by 'madparts'.<br/>\nId: " + idx + "\n" + parent_str
    for shape in shapes:
      if 'shape' in shape:
        if shape['shape'] == 'rect': self.rect(soup, package, shape)
        if shape['shape'] == 'circle': self.circle(soup, package, shape)
        if shape['shape'] == 'line': self.line(soup, package, shape)
      elif shape['type'] == 'label':
        self.label(soup, package, shape)

  def _check(self, soup):
    if soup.eagle == None:
      raise Exception("Unknown file format")
    v = soup.eagle.get('version')
    if v == None:
      raise Exception("Unknown file format (no eagle XML?)")
    if float(v) < 6:
      raise Exception("Eagle 6.0 or later is required.")
    return v

  def check(self, fn):
    soup = self.load(fn)
    v = self._check(soup)
    return "Eagle CAD %s library" % (v)

  def export(self, fn, shapes):
    soup = self.load(fn)
    self._check(soup) # just to be sure, check again
    # get name from meta from shapes:
    for shape in shapes:
      if shape['type'] == 'meta':
        name = eget(shape, 'name', 'Name not found')
        break
    # check if there is an existing package
    # and if so, replace it
    packages = soup.eagle.drawing.packages('package')
    found = None
    for package in packages:
      if package['name'] == name:
         found = package
         break
    if found != None:
      found.clear()
    else:
      found = soup.new_tag('package')
      soup.eagle.drawing.packages.append(found)
      found['name'] = name
    self.generate(soup, shapes, found)
    self.save(fn, soup)
