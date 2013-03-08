# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import StringIO, uuid, re, copy

from xml.sax.saxutils import escape

from bs4 import BeautifulSoup, Tag

from jydutil import *
import jydinter

# TODO: get from eagle XML isof hardcoded; 
# however in practice this is quite low prio as everybody probably
# uses the same layer numbers
def type_to_layer_number(layer):
  type_to_layer_number_dict = {
    'smd': 1,
    'pad': 17,
    'silk': 21,
    'name': 25,
    'value': 27,
    'docu': 51,
    }
  return type_to_layer_number_dict[layer]

def layer_number_to_type(layer):
  # assymetric
  layer_number_to_type_dict = {
    1: 'smd',
    16: 'pad',
    21: 'silk',
    25: 'silk',
    27: 'silk',
    29: 'stop',
    35: 'glue',
    39: 'keepout',
    41: 'restrict',
    43: 'vrestrict',
    51: 'docu',
    }
  return layer_number_to_type_dict[layer]

def _load_xml_file(fn):
  with open(fn) as f:
    return BeautifulSoup(f, "xml")
  
def _save_xml_file(fn, soup):
  with open(fn, 'w+') as f:
    f.write(str(soup))

def _check_xml(soup):
  if soup.eagle == None:
    raise Exception("Unknown file format")
  v = soup.eagle.get('version')
  if v == None:
    raise Exception("Unknown file format (no eagle XML?)")
  if float(v) < 6:
    raise Exception("Eagle 6.0 or later is required.")
  return v

def check_xml_file(fn):
  soup = _load_xml_file(fn)
  v = _check_xml(soup)
  return "Eagle CAD %s library" % (v)


### EXPORT

class Export:

  def __init__(self, fn):
    self.fn = fn
    self.soup = _load_xml_file(fn)
    _check_xml(self.soup)

  def save(self):
    _save_xml_file(self.fn, self.soup)

  def export_footprint(self, inter):
    meta = jydinter.get_meta(inter)
    name = eget(meta, 'name', 'Name not found')
    # check if there is an existing package
    # and if so, replace it
    packages = self.soup.eagle.drawing.packages('package')
    package = None
    for some_package in packages:
      if some_package['name'] == name:
        package = package
        break
    if package != None:
      package.clear()
    else:
      package = self.soup.new_tag('package')
      self.soup.eagle.drawing.packages.append(package)
      package['name'] = name

    def pad(shape, layer):
      pad = self.soup.new_tag('pad')
      pad['name'] = shape['name']
      pad['layer'] = type_to_layer_number('pad')
      pad['x'] = fget(shape, 'x')
      pad['y'] = fget(shape, 'y')
      pad['drill'] = fget(shape, 'drill')
      pad['rot'] = "R%d" % (fget(shape, 'rot'))
      shape = 'circle'
      if 'shape' in pad: shape = pad['shape']
      if shape == 'circle':
        pad['shape'] = 'round'
        pad['diameter'] = pad['r']/2
      elif shape == 'octagon':
        pad['shape'] = 'octagon'
        pad['diameter'] = pad['r']/2
      elif shape == 'rect':
        ro = iget(shape, 'ro')
        if ro == 0: 
          res['shape'] = 'square'
          res['diameter'] = pad['dx']
        elif 'drill_dx' in shape:
          pad['shape'] = 'offset'
          pad['diameter'] = pad['dy']
        else:
          pad['shape'] = 'long'
          pad['diameter'] = pad['dy']
      package.append(pad)

    def smd(shape):
      smd = self.soup.new_tag('smd')
      smd['name'] = shape['name']
      smd['x'] = fget(shape, 'x')
      smd['y'] = fget(shape, 'y')
      smd['dx'] = fget(shape, 'dx')
      smd['dy'] = fget(shape, 'dy')
      smd['roundness'] = iget(shape, 'ro')
      smd['rot'] = "R%d" % (fget(shape, 'rot'))
      smd['layer'] = type_to_layer_number('smd')
      package.append(smd)

    def rect(shape, layer):
      rect = self.soup.new_tag('rectangle')
      rect['x1'] = fget(shape, 'x1')
      rect['y1'] = fget(shape, 'y1')
      rect['x2'] = fget(shape, 'x2')
      rect['y2'] = fget(shape, 'y2')
      rect['rot'] = "R%d" % (fget(shape, 'rot'))
      rect['layer'] = layer
      package.append(rect)

    def label(shape, layer):
      label = self.soup.new_tag('text')
      x = fget(shape,'x')
      y = fget(shape,'y')
      dy = fget(shape,'dy', 1)
      s = shape['value']
      if s == "NAME": 
        s = ">NAME"
        layer = type_to_layer_number('name')
      if s == "VALUE": 
        s = ">VALUE"
        layer = type_to_layer_number('value')
      label['x'] = x - len(s)*dy/2
      label['y'] = y - dy/2
      label['size'] = dy
      label['layer'] = layer
      label.string = s
      package.append(label)
    
    def disc(shape, layer):
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
      # a disc is just a circle with a
      # clever radius and width
      disc = self.soup.new_tag('circle')
      disc['x'] = x
      disc['y'] = y
      disc['radius'] = r/2
      disc['width'] = r/2
      disc['layer'] = layer
      package.append(disc)
  
    def circle(shape, layer):
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
      w = fget(shape,'w')
      circle = self.soup.new_tag('circle')
      circle['x'] = x
      circle['y'] = y
      circle['radius'] = r
      circle['width'] = w
      circle['layer'] = layer
      package.append(circle)

    def line(shape, layer):
      x1 = fget(shape, 'x1')
      y1 = fget(shape, 'y1')
      x2 = fget(shape, 'x2')
      y2 = fget(shape, 'y2')
      w = fget(shape, 'w')
      line = self.soup.new_tag('wire')
      line['x1'] = x1
      line['y1'] = y1
      line['x2'] = x2
      line['y2'] = y2
      line['width'] = w
      line['layer'] = layer
      package.append(line)
  
    def silk(shape):
      if not 'shape' in shape: return
      layer = type_to_layer_number(shape['type'])
      s = shape['shape']
      if s == 'line': line(shape, layer)
      elif s == 'circle': circle(shape, layer)
      elif s == 'disc': disc(shape, layer)
      elif s == 'label': circle(shape, layer)
      elif s == 'rect': rect(shape, layer)

    def unknown(shape):
      pass

    idx = eget(meta, 'id', 'Id not found')
    desc = oget(meta, 'desc', '')
    parent_idx = oget(meta, 'parent', None)
    description = self.soup.new_tag('description')
    package.append(description)
    parent_str = ""
    if parent_idx != None:
      parent_str = " parent: %s" % parent_idx
    description.string = desc + "\n<br/><br/>\nGenerated by 'madparts'.<br/>\nId: " + idx   +"\n" + parent_str
    # TODO rework to be shape+type based ?
    for shape in inter:
      if 'type' in shape:
        {
          'pad': pad,
          'silk': silk,
          'docu': silk,
          'smd': smd,
          }.get(shape['type'], unknown)(shape)
        # TODO octagon

### IMPORT

class Import:

  def __init__(self, fn):
    self.soup = _load_xml_file(fn)
    _check_xml(self.soup)

  def list_names(self):
    packages = self.soup.eagle.drawing.packages('package')
    def desc(p):
      if p.description != None: return p.description.string
      else: return None
    return [(p['name'], desc(p)) for p in packages]

  def import_footprint(self, name):

    def package_has_name(tag):
      if tag.name == 'package' and tag.has_key('name'):
        n = tag['name']
        if n == name:
          return True
        return False

    [package] = self.soup.find_all(package_has_name)
    meta = {}
    meta['type'] = 'meta'
    meta['name'] = name
    meta['id'] = uuid.uuid4().hex
    meta['desc'] = None
    l = [meta]

    def clean_name(name):
      if len(name) > 2 and name[0:1] == 'P$':
        name = name[2:]
        # this might cause name clashes :(
        # get rid of @ suffixes
      return re.sub('@\d+$', '', name)

    def text(text):
      res = {}
      res['type'] = 'silk'
      res['shape'] = 'label'
      s = text.string
      layer = int(text['layer'])
      size = float(text['size'])
      y = float(text['y']) + size/2
      x = float(text['x']) + len(s)*size/2
      res['value'] = s
      if layer == 25 and s == '>NAME':
        res['value'] = 'NAME'
      elif layer == 27 and s == '>VALUE':
        res['value'] = 'VALUE'
      if x != 0: res['x'] = x
      if y != 0: res['y'] = y
      if text.has_key('size'):
        res['dy'] = text['size']
      return res

    def smd(smd):
      res = {}
      res['type'] = 'smd'
      res['shape'] = 'rect'
      res['name'] = clean_name(smd['name'])
      res['dx'] = float(smd['dx'])
      res['dy'] = float(smd['dy'])
      res['x'] = float(smd['x'])
      res['y'] = float(smd['y'])
      if smd.has_key('rot'):
        res['rot'] = int(smd['rot'][1:])
      if smd.has_key('roundness'):
        res['ro'] = smd['roundness']
      return res

    def rect(rect):
      res = {}
      res['type'] = layer_number_to_type(int(rect['layer']))
      res['shape'] = 'rect'
      res['x1'] = float(rect['x1'])
      res['y1'] = float(rect['y1'])
      res['x2'] = float(rect['x2'])
      res['y2'] = float(rect['y2'])
      if rect.has_key('rot'):
        res['rot'] = int(rect['rot'][1:])
      return res

    def wire(wire):
      res = {}
      res['type'] = layer_number_to_type(int(wire['layer']))
      res['shape'] = 'line'
      res['x1'] = float(wire['x1'])
      res['y1'] = float(wire['y1'])
      res['x2'] = float(wire['x2'])
      res['y2'] = float(wire['y2'])
      res['w'] = float(wire['width'])
      return res

    def circle(circle):
      res = {}
      res['type'] = layer_number_to_type(int(circle['layer']))
      res['shape'] = 'circle'
      w =float(circle['width'])
      res['w'] = w
      res['r'] = float(circle['radius']) + w/2
      res['x'] = float(circle['x'])
      res['y'] = float(circle['y'])
      return res

    def description(desc):
      meta['desc'] = desc.string
      return None

    def pad(pad):
      res = {}
      res['type'] = 'pad'
      res['name'] = clean_name(pad['name'])
      res['x'] = pad['x']
      res['y'] = pad['y']
      drill = float(pad['drill'])
      res['drill'] = drill
      if pad.has_key('diameter'):
        dia = float(pad['diameter'])
      else:
        dia = res['drill'] * 1.5
      if pad.has_key('rot'):
        res['rot'] = int(pad['rot'][1:])
      shape = 'round'
      if pad.has_key('shape'): shape = pad['shape']
      if shape == 'round':
        res['shape'] = 'circle'
        res['r'] = 0.0
        if dia/2 > drill: res['r'] = dia/2
      elif shape == 'square':
        res['shape'] = 'rect'
        res['dx'] = dia
        res['dy'] = dia
      elif shape == 'long':
        res['shape'] = 'rect'
        res['ro'] = 100
        res['dx'] = 2*dia
        res['dy'] = dia
      elif shape == 'offset':
        res['shape'] = 'rect'
        res['ro'] = 100
        res['dx'] = 2*dia
        res['dy'] = dia
        res['drill_dx'] = -dia/2
      elif shape == 'octagon':
        res['shape'] = 'octagon'
        res['r'] = dia/2
      return res
      

    def unknown(x):
      res = {}
      res['type'] = 'unknown'
      res['value'] = str(x)
      res['shape'] = 'unknown'
      return res

    for x in package.contents:
      if type(x) == Tag:
        print x.name
        result = {
          'circle': circle,
          'description': description,
          'pad': pad,
          'smd': smd,
          'text': text,
          'wire': wire,
          'rectangle': rect,
          }.get(x.name, unknown)(x)
        if result != None: l.append(result)
    return l

