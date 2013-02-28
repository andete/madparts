# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import StringIO, uuid

from xml.sax.saxutils import escape

from bs4 import BeautifulSoup, Tag

from jydutil import *

type_to_layer_number_dict = {
  'smd': 1,
  'silk': 21,
  'name': 25,
  'value': 27,
}

layer_number_to_type_dict = dict([(y,x) for (x,y) in type_to_layer_number_dict.items()])

# TODO: get from eagle XML isof hardcoded; 
# however in practice this is quite low prio as everybody probably
# uses the same layer numbers
def type_to_layer_number(layer):
  return type_to_layer_number_dict[layer]

def layer_number_to_type(layer):
  return layer_number_to_type_dict[layer]

# this can still use plenty of abstraction
def rect(soup, package, shape):
  smd = soup.new_tag('smd')
  smd['name'] = shape['name']
  smd['x'] = fget(shape, 'x')
  smd['y'] = fget(shape, 'y')
  smd['dx'] = fget(shape, 'dx')
  smd['dy'] = fget(shape, 'dy')
  smd['roundness'] = iget(shape, 'ro')
  smd['rot'] = "R%d" % (fget(shape, 'rot'))
  smd['layer'] = type_to_layer_number(shape['type'])
  package.append(smd)

def label(soup, package, shape):
  label = soup.new_tag('text')
  x = fget(shape,'x')
  y = fget(shape,'y')
  dy = fget(shape,'dy', 1)
  s = shape['value']
  if s == "NAME": 
    s = ">NAME"
  if s == "VALUE": 
    s = ">VALUE"
  label['x'] = x - len(s)*dy/2
  label['y'] = y - dy/2
  label['size'] = dy
  label['layer'] = type_to_layer_number(shape['type'])
  label.string = s
  package.append(label)
  
def circle(soup, package, shape):
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
  w = 0.25 # TODO
  circle = soup.new_tag('circle')
  circle['x'] = x
  circle['y'] = y
  circle['radius'] = (r-w/2)
  circle['width'] = w
  circle['layer'] = type_to_layer_number(shape['type'])
  package.append(circle)

def line(soup, package, shape):
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
  line['layer'] = type_to_layer_number(shape['type'])
  package.append(line)

def load(fn):
  with open(fn) as f:
    return BeautifulSoup(f, "xml")

def save(fn, soup):
  with open(fn, 'w+') as f:
    f.write(str(soup))
  
def generate(soup, shapes, package):
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
  description.string = desc + "\n<br/><br/>\nGenerated by 'madparts'.<br/>\nId: " + idx +"\n" + parent_str
  for shape in shapes:
    if 'shape' in shape:
      if shape['shape'] == 'rect': rect(soup, package, shape)
      if shape['shape'] == 'circle': circle(soup, package, shape)
      if shape['shape'] == 'line': line(soup, package, shape)
      if shape['shape'] == 'label': label(soup, package, shape)

def _check(soup):
  if soup.eagle == None:
    raise Exception("Unknown file format")
  v = soup.eagle.get('version')
  if v == None:
    raise Exception("Unknown file format (no eagle XML?)")
  if float(v) < 6:
    raise Exception("Eagle 6.0 or later is required.")
  return v

def check(fn):
  soup = load(fn)
  v = _check(soup)
  return "Eagle CAD %s library" % (v)

def export(fn, shapes):
  soup = load(fn)
  _check(soup) # just to be sure, check again
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
  generate(soup, shapes, found)
  save(fn, soup)

def list_names(fn):
  soup = load(fn)
  v = _check(soup)
  packages = soup.eagle.drawing.packages('package')
  def desc(p):
    if p.description != None: return p.description.string
    else: return None
  return ([(p['name'], desc(p)) for p in packages], soup)

def handle_text(text, meta):
  res = {}
  res['type'] = 'silk'
  res['shape'] = 'label'
  s = text.string
  layer = int(text['layer'])
  size = float(text['size'])
  y = float(text['y'])
  x = float(text['x']) + len(s)*size/2
  res['value'] = s
  if layer == 25 and s == '>NAME':
    res['value'] = 'NAME'
  elif layer == 27 and s == '>VALUE':
    res['value'] = 'VALUE'
  if x != 0: res['x'] = x
  if y != 0: res['y'] = y
  return res

# {'name': '5', 'type': 'smd', 'shape': 'rect', 'dx': 1.67, 'dy': 0.36, 'y': -0.4, 'x': -4.5, 'ro': 50, 'adj': 0}

def handle_smd(smd, meta):
  res = {}
  res['type'] = 'smd'
  res['name'] = smd['name']
  res['dx'] = float(smd['dx'])
  res['dy'] = float(smd['dy'])
  res['x'] = float(smd['x'])
  res['y'] = float(smd['y'])
  res['ro'] = smd['roundness']
  rot = smd['rot']
  if rot != None:
    res['rot'] = int(rot[1:])
  ro = smd['roundness']
  if ro != None:
    res['ro'] = int(ro)
  return res

def handle_wire(wire, meta):
  res = {}
  res['type'] = layer_number_to_type(int(wire['layer']))
  res['shape'] = 'line'
  res['x1'] = float(wire['x1'])
  res['y1'] = float(wire['y1'])
  res['x2'] = float(wire['x2'])
  res['y2'] = float(wire['y2'])
  res['w'] = float(wire['width'])
  return res

def handle_circle(circle, meta):
  res = {}
  res['type'] = layer_number_to_type(int(circle['layer']))
  res['shape'] = 'circle'
  w = 0.25 # TODO
  res['r'] = float(circle['radius']) + w/2
  res['x'] = float(circle['x'])
  res['y'] = float(circle['y'])
  return res

def handle_description(desc, meta):
  meta['desc'] = desc.string
  return None

def handle_unknown(x, meta):
  raise Exception("unknown element %s" % (x))

def import_footprint(soup, name):
  def package_has_name(tag):
    if tag.name == 'package' and tag.has_key('name'):
      n = tag['name']
      if n == name:
        return True
    return False
  [package] = soup.find_all(package_has_name)
  meta = {}
  meta['type'] = 'meta'
  meta['name'] = name
  meta['id'] = uuid.uuid4().hex
  l = [meta]
  for x in package.contents:
    if type(x) == Tag:
      result = {
        'text': handle_text,
        'smd': handle_smd,
        'wire': handle_wire,
        'circle': handle_circle,
        'description': handle_description,
      }.get(x.name, handle_unknown)(x, meta)
      if result != None: l.append(result)
  return l
