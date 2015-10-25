# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import uuid, re, copy, math

from bs4 import BeautifulSoup, Tag

from mutil.mutil import *

from inter import inter

# TODO: get from eagle XML isof hardcoded; 
# however in practice this is quite low prio as everybody probably
# uses the same layer numbers
def type_to_layer_number(layer):
  type_to_layer_number_dict = {
    'smd': 1,
    'cu': 1,
    'pad': 17,
    'silk': 21,
    'name': 25,
    'value': 27,
    'stop': 29,
    'glue': 35,
    'keepout': 39,
    'restrict': 41,
    'vrestrict': 43,
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
    40: 'keepout',
    41: 'restrict',
    43: 'vrestrict',
    51: 'docu',
    }
  return layer_number_to_type_dict[layer]

def _load_xml_file(fn):
  with open(fn) as f:
    return BeautifulSoup(f, 'xml')
  
def _save_xml_file(fn, soup):
  with open(fn, 'w+') as f:
    f.write(str(soup))

def _check_xml(soup):
  if soup.eagle == None:
    raise Exception("Unknown file format")
  v = soup.eagle.get('version')
  if v == None:
    raise Exception("Unknown file format (no eagle XML?)")
  if int(v.split('.', 1)[0]) < 6:
    raise Exception("Eagle 6.0 or later is required.")
  return v

def check_xml_file(fn):
  soup = _load_xml_file(fn)
  v = _check_xml(soup)
  return "Eagle CAD %s library" % (v)

def detect(fn):
  try:
    soup = _load_xml_file(fn)
    return str(_check_xml(soup))
  except:
    return None

### EXPORT

class Export:

  def __init__(self, fn):
    self.fn = fn
    self.soup = _load_xml_file(fn)
    _check_xml(self.soup)

  def save(self):
    _save_xml_file(self.fn, self.soup)

  def get_data(self):
   return str(self.soup)

  # remark that this pretty formatting is NOT what is used in the final
  # eagle XML as eagle does not get rid of heading and trailing \n and such
  def get_pretty_data(self):
   return str(self.soup.prettify())

  def get_pretty_footprint(self, eagle_name):
    packages = self.soup.eagle.drawing.packages('package')
    for some_package in packages:
      if some_package['name'].lower() == eagle_name.lower():
        return str(some_package.prettify())
    raise Exception("Footprint not found")
   

  def export_footprint(self, interim):
    # make a deep copy so we can make mods without harm
    interim = copy.deepcopy(interim)
    interim = self.add_ats_to_names(interim)
    interim = clean_floats(interim)
    meta = inter.get_meta(interim)
    name = eget(meta, 'name', 'Name not found')
    # make name eagle compatible
    name = re.sub(' ','_',name)
    # check if there is an existing package
    # and if so, replace it
    packages = self.soup.eagle.drawing.packages('package')
    package = None
    for some_package in packages:
      if some_package['name'].lower() == name.lower():
        package = some_package
        package.clear()
        break
    if package == None:
      package = self.soup.new_tag('package')
      self.soup.eagle.drawing.packages.append(package)
      package['name'] = name

    def pad(shape):
      pad = self.soup.new_tag('pad')
      pad['name'] = shape['name']
      # don't set layer in a pad, it is implicit
      pad['x'] = fget(shape, 'x')
      pad['y'] = fget(shape, 'y')
      drill = fget(shape, 'drill')
      pad['drill'] = drill
      pad['rot'] = "R%d" % (fget(shape, 'rot'))
      r = fget(shape, 'r')
      shape2 = 'disc' # disc is the default
      if 'shape' in shape:
        shape2 = shape['shape']
      if shape2 == 'disc':
        pad['shape'] = 'round'
        if f_neq(r, drill*1.5):
          pad['diameter'] = r*2
      elif shape2 == 'octagon':
        pad['shape'] = 'octagon'
        if f_neq(r, drill*1.5):
          pad['diameter'] = r*2
      elif shape2 == 'rect':
        ro = iget(shape, 'ro')
        if ro == 0: 
          pad['shape'] = 'square'
          if f_neq(shape['dx'], drill*1.5):
            pad['diameter'] = float(shape['dx'])
        elif 'drill_dx' in shape:
          pad['shape'] = 'offset'
          if f_neq(shape['dy'], drill*1.5):
            pad['diameter'] = float(shape['dy'])
        else:
          pad['shape'] = 'long'
          if f_neq(shape['dy'], drill*1.5):
            pad['diameter'] = float(shape['dy'])
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

    def hole(shape):
      hole = self.soup.new_tag('hole')
      hole['drill'] = fget(shape, 'drill')
      hole['x'] = fget(shape, 'x')
      hole['y'] = fget(shape, 'y')
      package.append(hole)

    def rect(shape, layer):
      rect = self.soup.new_tag('rectangle')
      x = fget(shape, 'x')
      y = fget(shape, 'y')
      dx = fget(shape, 'dx')
      dy = fget(shape, 'dy')
      rect['x1'] = x - dx/2
      rect['x2'] = x + dx/2
      rect['y1'] = y - dy/2
      rect['y2'] = y + dy/2
      rect['rot'] = "R%d" % (fget(shape, 'rot'))
      rect['layer'] = layer
      package.append(rect)

    def label(shape, layer):
      label = self.soup.new_tag('text')
      x = fget(shape,'x')
      y = fget(shape,'y')
      dy = fget(shape,'dy', 1)
      s = shape['value'].upper()
      if s == "NAME": 
        s = ">NAME"
        layer = type_to_layer_number('name')
      if s == "VALUE": 
        s = ">VALUE"
        layer = type_to_layer_number('value')
      label['x'] = x
      label['y'] = y
      label['size'] = dy
      label['layer'] = layer
      label['align'] = 'center'
      label.string = s
      package.append(label)
    
    # a disc is just a circle with a clever radius and width
    def disc(shape, layer):
      r = fget(shape, 'r')
      rx = fget(shape, 'rx', r)
      ry = fget(shape, 'ry', r)
      x = fget(shape,'x')
      y = fget(shape,'y')
      disc = self.soup.new_tag('circle')
      disc['x'] = x
      disc['y'] = y
      disc['radius'] = r/2
      disc['width'] = r/2
      disc['layer'] = layer
      package.append(disc)
  
    def circle(shape, layer):
      r = fget(shape, 'r')
      rx = fget(shape, 'rx', r)
      ry = fget(shape, 'ry', r)
      x = fget(shape,'x')
      y = fget(shape,'y')
      w = fget(shape,'w')
      if 'a1' in shape or 'a2' in shape:
        wire = self.soup.new_tag('wire')
        a1 = fget(shape, 'a1')
        a2 = fget(shape, 'a2')
        wire['width'] = w
        wire['curve'] = a2-a1
        a1 = a1 * math.pi / 180
        a2 = a2 * math.pi / 180
        wire['x1'] = x + r * math.cos(a1)
        wire['y1'] = y + r * math.sin(a1)
        wire['x2'] = x + r * math.cos(a2)
        wire['y2'] = y + r * math.sin(a2)
        wire['layer'] = layer
        package.append(wire)
      else:
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
      if 'curve' in shape:
        if shape['curve'] != 0.0:
          line['curve'] = fget(shape, 'curve')
      package.append(line)
  
    # eagle polygon format is somewhat wierd
    # each vertex is actually a starting point towards the next
    # where the last one is a starting point around towards the first
    #  <polygon width="0.127" layer="21">
    #  <vertex x="-1" y="-1"/>
    #  <vertex x="-1" y="1"/>
    #  <vertex x="0" y="1" curve="-90"/>
    #  <vertex x="1" y="0" curve="-90"/>
    #  <vertex x="0" y="-1"/>
    #  </polygon>
    def polygon(shape, layer):
      p = self.soup.new_tag('polygon')
      p['width'] = fget(shape, 'w')
      p['layer'] = layer
      for v in shape['v']:
        vert = self.soup.new_tag('vertex')
        vert['x'] = fget(v, 'x1')
        vert['y'] = fget(v, 'y1')
        curve = fget(v, 'curve')
        if curve != 0.0:
          vert['curve'] = fget(v, 'curve')
        p.append(vert)
      package.append(p)

    def silk(shape):
      if not 'shape' in shape: return
      layer = type_to_layer_number(shape['type'])
      s = shape['shape']
      if s == 'line' or s == 'vertex': line(shape, layer)
      elif s == 'circle': circle(shape, layer)
      elif s == 'disc': disc(shape, layer)
      elif s == 'label': label(shape, layer)
      elif s == 'rect': rect(shape, layer)
      elif s == 'polygon': polygon(shape, layer)

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
    for shape in interim:
      if 'type' in shape:
        {
          'pad': pad,
          'silk': silk,
          'cu': silk,
          'docu': silk,
          'keepout': silk,
          'stop': silk,
          'restrict': silk,
          'vrestrict': silk,
          'smd': smd,
          'hole': hole,
          }.get(shape['type'], unknown)(shape)
    return name

  def add_ats_to_names(self, interim):
    t = {}
    for x in interim:
      if x['type'] == 'smd' or x['type'] == 'pad':
        name = x['name']
        if not name in t:
          t[name] = 0
        t[name] = t[name] + 1
    multi_names = {}
    for k in t.keys():
      if t[k] > 1:
        multi_names[k] = 1
    def adapt(x):
      if x['type'] == 'smd' or x['type'] == 'pad':
        name = re.sub(' ','_', str(x['name']))
        if name in multi_names:
          x['name'] = "%s@%d" % (name, multi_names[name])
          multi_names[name] = multi_names[name] + 1
      return x
    return [adapt(x) for x in interim]

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

  def list(self):
    names = map(lambda (a,_): a, self.list_names())
    for name in names: print name

  def import_footprint(self, name):

    packages = self.soup.eagle.drawing.packages('package')
    package = None
    for p in packages:
       if p['name'] == name:
         package = p
         break
    if package == None:
      raise Exception("footprint not found %s " % (name))
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
      align = 'bottom-left' # eagle default
      if text.has_attr('align'):
        align = text['align']
      if align == 'center':
        x = float(text['x'])
        y = float(text['y'])
      elif align == 'bottom-left':
        x = float(text['x']) + len(s)*size/2
        y = float(text['y']) + size/2
      else:
        # TODO deal with all other cases; assuming center
        # eagle supports: bottom-left | bottom-center | bottom-right | center-left | center | center-right | top-left | top-center | top-right
        x = float(text['x']) + len(s)*size/2
        y = float(text['y']) + size/2
      res['value'] = s
      if layer == 25 and s.upper() == '>NAME':
        res['value'] = 'NAME'
      elif layer == 27 and s.upper() == '>VALUE':
        res['value'] = 'VALUE'
      if x != 0: res['x'] = x
      if y != 0: res['y'] = y
      if text.has_attr('size'):
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
      if smd.has_attr('rot'):
        res['rot'] = int(smd['rot'][1:])
      if smd.has_attr('roundness'):
        if smd['roundness'] != '0':
          res['ro'] = smd['roundness']
      return res

    def rect(rect):
      res = {}
      res['type'] = layer_number_to_type(int(rect['layer']))
      res['shape'] = 'rect'
      x1 = float(rect['x1'])
      y1 = float(rect['y1'])
      x2 = float(rect['x2'])
      y2 = float(rect['y2'])
      res['x'] = (x1+x2)/2
      res['y'] = (y1+y2)/2
      res['dx'] = abs(x1-x2)
      res['dy'] = abs(y1-y2)
      if rect.has_attr('rot'):
        res['rot'] = int(rect['rot'][1:])
      return res

    def wire(wire):
      res = {}
      res['type'] = layer_number_to_type(int(wire['layer']))
      res['shape'] = 'vertex'
      res['x1'] = float(wire['x1'])
      res['y1'] = float(wire['y1'])
      res['x2'] = float(wire['x2'])
      res['y2'] = float(wire['y2'])
      res['w'] = float(wire['width'])
      # assymetry here: an Arc exported will come back as
      # a curved vertex
      if wire.has_attr('curve'):
        res['curve'] = float(wire['curve'])
      return res

    def circle(circle):
      res = {}
      res['type'] = layer_number_to_type(int(circle['layer']))
      res['shape'] = 'circle'
      w = float(circle['width'])
      r = float(circle['radius'])
      res['x'] = float(circle['x'])
      res['y'] = float(circle['y'])
      if w == r:
        res['shape'] = 'disc'
        res['r'] = r * 2
      else:
        res['w'] = w
        res['r'] = r
      return res

    def description(desc):
      meta['desc'] = desc.string
      return None

    def pad(pad):
      res = {}
      res['type'] = 'pad'
      res['name'] = clean_name(pad['name'])
      res['x'] = float(pad['x'])
      res['y'] = float(pad['y'])
      drill = float(pad['drill'])
      res['drill'] = drill
      if pad.has_attr('diameter'):
        dia = float(pad['diameter'])
      else:
        dia = res['drill'] * 1.5
      if pad.has_attr('rot'):
        res['rot'] = int(pad['rot'][1:])
      shape = 'round'
      if pad.has_attr('shape'):
        shape = pad['shape']
      if shape == 'round':
        res['shape'] = 'disc'
        res['r'] = 0.0
        #if dia/2 > drill:
        res['r'] = dia/2
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
     
    def hole(x):
      res = {'type':'hole', 'shape':'hole'}
      res['drill'] = fget(x,'drill')
      res['x'] = fget(x,'x')
      res['y'] = fget(x,'y')
      return res

    def polygon(x):
      res = { 'shape':'polygon' }
      res['w'] = float(x['width'])
      res['type'] = layer_number_to_type(int(x['layer']))
      res['v'] = []
      for e in x.find_all('vertex'):
        vert = { 'shape':'vertex' }
        vert['x1'] = float(e['x'])
        vert['y1'] = float(e['y'])
        if e.has_attr('curve'):
          vert['curve'] = float(e['curve'])
        res['v'].append(vert)
      l = len(res['v'])
      for i in range(0, l):
        res['v'][i]['x2'] = res['v'][i-l+1]['x1']
        res['v'][i]['y2'] = res['v'][i-l+1]['y1']
      return res

    def unknown(x):
      res = {}
      res['type'] = 'unknown'
      res['value'] = str(x)
      res['shape'] = 'unknown'
      return res

    for x in package.contents:
      if type(x) == Tag:
        result = {
          'circle': circle,
          'description': description,
          'pad': pad,
          'smd': smd,
          'text': text,
          'wire': wire,
          'rectangle': rect,
          'polygon': polygon,
          'hole': hole,
          }.get(x.name, unknown)(x)
        if result != None: l.append(result)
    return clean_floats(l)

