# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import glob
import math
import os.path
import uuid

import sexpdata
from sexpdata import Symbol

from mutil.mutil import *
from inter import inter

def S(v):
  return Symbol(str(v))

def type_to_layer_name(layer):
  return {
    'smd': 'F.Cu', # these two are normally
    'pad': 'F.Cu', # not used like this
    'silk': 'F.SilkS',
    'name': 'F.SilkS',
    'value': 'Dwgs.User',
    'stop': 'F.Mask',
    'glue': 'F.Adhes',
    'docu': 'Dwgs.User',
    }.get(layer)

def layer_name_to_type(name):
   return {
    'F.SilkS': 'silk',
    'Dwgs.User': 'docu',
    'F.Mask': 'stop',
    'F.Adhes': 'glue',
   }.get(name)


def detect(fn):
  if os.path.isdir(fn) and '.pretty' in fn:
    return "3"
  try:
    l = sexpdata.load(open(fn, 'r'))
    if (l[0] == S('module')): return "3"
    return None
  except IOError:
    # allow new .kicad_mod files!
    if '.kicad_mod' in fn: return "3"
    return None
  except:
    return None

def _convert_sexp_symbol(d):
  if ("value" in dir(d)):
    return d.value()
  else:
    return d

def _convert_sexp_symbol_to_string(d):
  return str(_convert_sexp_symbol(d))

class Export:

  def __init__(self, fn):
    self.fn = fn

  def export_footprint(self, interim):
    meta = inter.get_meta(interim)
    name = eget(meta, 'name', 'Name not found')
    idx = eget(meta, 'id', 'Id not found')
    descr = oget(meta, 'desc', '')
    parent_idx = oget(meta, 'parent', None)
    l = [
      S('module'),
      S(name),
      [S('layer'), S('F.Cu')],
      [S('descr'), descr],
    ]
    
    def pad(shape, smd=False):
      l = [S('pad'), S(shape['name'])]
      if smd:
        l.append(S('smd'))
      else:
        l.append(S('thru_hole'))
      shape2 = 'disc' # disc is the default
      if 'shape' in shape:
        shape2 = shape['shape']
      r = fget(shape, 'r')
      if shape2 == 'disc':
        l.append(S('circle'))
        l.append([S('size'), r, r])
      elif shape2 == 'rect':
        ro = iget(shape, 'ro')
        if ro == 0:
          l.append(S('rect'))
        else:
          l.append(S('oval'))
        l.append([S('size'), fget(shape, 'dx'), fget(shape, 'dy')])
      else:
        raise Exception("%s shaped pad not supported in kicad" % (shape2))
      l.append([S('at'), fget(shape, 'x'), -fget(shape, 'y'), iget(shape, 'rot')])
      if smd:
        l.append([S('layers'), S('F.Cu'), S('F.Paste'), S('F.Mask')])
      else:
        l.append([S('layers'), S('*.Cu'), S('*.Mask')])
      if not smd:
        l2 = [S('drill'), fget(shape, 'drill')]
        if 'drill_dx' in shape or 'drill_dy' in shape:
          l2.append([S('offset'), fget(shape, 'drill_dx'), fget(shape, 'drill_dy')])
        l.append(l2)
      return l
    
    #(fp_line (start -2.54 -1.27) (end 2.54 -1.27) (layer F.SilkS) (width 0.381))
    def line(shape, layer):
      l = [S('fp_line')] 
      l.append([S('start'), fget(shape, 'x1'), -fget(shape, 'y1')])
      l.append([S('end'), fget(shape, 'x2'), -fget(shape, 'y2')])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), fget(shape, 'w')])
      return l

    # (fp_circle (center 5.08 0) (end 6.35 -1.27) (layer F.SilkS) (width 0.15))
    def circle(shape, layer):
      l = [S('fp_circle')]  
      x = fget(shape, 'x')
      y = -fget(shape, 'y')
      l.append([S('center'), x, y])
      r = fget(shape, 'r')
      l.append([S('end'), x+(r/math.sqrt(2)), y+(r/math.sqrt(2))])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), fget(shape, 'w')])
      return l

    # a disc is just a circle with a clever radius and width
    def disc(shape, layer):
      l = [S('fp_circle')] 
      x = fget(shape, 'x')
      y = -fget(shape, 'y')
      l.append([S('center'), x, y])
      r = fget(shape, 'r')
      rad = r/2
      l.append([S('end'), x+(rad/math.sqrt(2)), y+(rad/math.sqrt(2))])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), rad])
      return l

    # (fp_arc (start 7.62 0) (end 7.62 -2.54) (angle 90) (layer F.SilkS) (width 0.15))
    def arc(shape, layer):
      l = [S('fp_arc')] 
      l.append([S('start'), fget(shape, 'x1'), -fget(shape, 'y1')])
      l.append([S('end'), fget(shape, 'x2'), -fget(shape, 'y2')])
      l.append([S('angle'), fget(shape, 'a')])
      l.append([S('layer'), S(layer)])
      l.append([S('w'), fget(shape, 'w')])
      return l


    # (pad "" smd rect (at 1.27 0) (size 0.39878 0.8001) (layers F.SilkS))
    def rect(shape, layer):
      # TODO: Don't do this with a pad. Use a polygon
      l = [S('pad'), "", S('smd'), S('rect')] 
      l.append([S('at'), fget(shape, 'x'), -fget(shape, 'y'), iget(shape, 'rot')])
      l.append([S('size'), fget(shape, 'dx'), fget(shape, 'dy')])
      l.append([S('layers'), S(layer)])
      return l

    # (fp_text reference MYCONN3 (at 0 -2.54) (layer F.SilkS)
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    # (fp_text value SMD (at 0 2.54) (layer F.SilkS) hide
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    def label(shape, layer):
      s = shape['value'].upper()
      t = 'user'
      if s == 'VALUE': t = 'value'
      if s == 'NAME': t = 'reference'
      l = [S('fp_text'), S(t), S(shape['value'])]
      if (('rot' in shape) and (fget(shape, 'rot') != 0.0)):
        l.append([S('at'), fget(shape, 'x'), -fget(shape, 'y'), fget(shape, 'rot')])
      else:
        l.append([S('at'), fget(shape, 'x'), -fget(shape, 'y')])
      l.append([S('layer'), S(layer)])
      if s == 'VALUE':
        l.append(S('hide'))
      dy = fget(shape, 'dy', 1/1.6)
      th = fget(shape, 'w', 0.1)
      l.append([S('effects'), 
                [S('font'), [S('size'), dy, dy], [S('thickness'), th]]])
      return l

    def silk(shape):
      if not 'shape' in shape: return None
      layer = type_to_layer_name(shape['type'])
      s = shape['shape']
      if s == 'line': return line(shape, layer)
      elif s == 'arc': return arc(shape, layer)
      elif s == 'circle': return circle(shape, layer)
      elif s == 'disc': return disc(shape, layer)
      elif s == 'label': return label(shape, layer)
      elif s == 'rect': return rect(shape, layer)

    def unknown(shape):
      return None

    for shape in interim:
      if 'type' in shape:
        l2 = {
          'pad': pad,
          'silk': silk,
          'docu': silk,
          'keepout': unknown,
          'stop': silk,
          'glue': silk,
          'restrict': unknown,
          'vrestrict': unknown,
          'smd': lambda s: pad(s, smd=True),
          }.get(shape['type'], unknown)(shape)
        if l2 != None:
         l.append(l2)
    self.data = l
    self.name = name
    return name

  def save(self):
    if os.path.isdir(self.fn) and '.pretty' in self.fn:
      name = self.name.replace(' ', '_')
      fn = os.path.join(self.fn, name + '.kicad_mod')
    else:
      fn = self.fn
    with open(fn, 'w+') as f:
      sexpdata.dump(self.data, f)

  def get_string(self):
    return sexpdata.dumps(self.data)

class Import:

  def __init__(self, fn):
    self.fn = fn
    if os.path.isdir(self.fn) and '.pretty' in self.fn:
      self.files = glob.glob(self.fn + '/*.kicad_mod')
    else:
      self.files = [self.fn]

  def list_names(self):
    l = []
    for f in self.files:
      s = sexpdata.load(open(f, 'r'))
      name = _convert_sexp_symbol_to_string(s[1])
      fp = self._import_footprint(s)
      desc = None
      for x in fp:
         if x['type'] == 'meta':
           if 'desc' in x:
             desc = x['desc']
             break
      l.append((name, desc))
      return l

  def list(self):
    for f in self.files:
      l = sexpdata.load(open(f, 'r'))
      print _convert_sexp_symbol_to_string(l[1])

  def import_footprint(self, name):
    s = None
    for f in self.files:
      s = sexpdata.load(open(f, 'r'))
      if _convert_sexp_symbol_to_string(s[1]) == name:
        break
    if s is None:
      raise Exception("Footprint %s not found" % (name))
    return self._import_footprint(s)

  def _import_footprint(self, s):
    meta = {}
    meta['type'] = 'meta'
    meta['name'] = _convert_sexp_symbol_to_string(s[1])
    meta['id'] = uuid.uuid4().hex
    meta['desc'] = None
    l = [meta]

    def get_sub(x, name):
      print "X: "
      print x
      for e in x:
        if ("__len__" not in dir(e)):
          continue # Ignore objects without length
        if (len(e) == 0):
          continue # Ignore empty
        if _convert_sexp_symbol_to_string(e[0]) == name:
          return list(map(_convert_sexp_symbol, e[1:]))
      return None

    def has_sub(x, name):
      for e in x:
        if ("__len__" not in dir(e)):
          continue # Ignore objects without length
        if (len(e) == 0):
          continue # Ignore empty
        if _convert_sexp_symbol_to_string(e[0]) == name:
          return True
      return False
      
    def get_single_element_sub(x, name, default=None):
      sub = get_sub(x, name)
      if (sub != None):
        if (len(sub) != 1):
          raise Exception("Unexpected multi-element '%s' sub: %s" % (name, str(sub)))
        return sub[0]
      return default
      
    def get_layer_sub(x, default=None):
      layer = get_single_element_sub(x, 'layer')
      if (layer != None):
        return layer_name_to_type(layer)
      return default
    
    def get_layers_sub(x, default=None):
      layers = get_sub(x, 'layers')
      if (layers != None):
        return list(map(layer_name_to_type, layers))
      return default

    def get_at_sub(x):
      sub = get_sub(x, 'at')
      if (sub is None):
        raise Exception("Expected 'at' element in %s" % (str(x)))
      if (len(sub) == 2):
        [x1, y1] = sub
        rot = 0
      elif (len(sub) == 3):
        [x1, y1, rot] = sub
      else:
        raise Exception("Invalid 'at' element in %s" % (str(x)))      
      return (x1, y1, rot)

    def descr(x):
      meta['desc'] = x[1]

    # (pad 1 smd rect (size 1.1 1.0) (at -0.85 -0.0 0) (layers F.Cu F.Paste F.Mask))
    # (pad 5 thru_hole circle (size 0.75 0.75) (at 1.79 3.155 0) (layers *.Cu *.Mask) (drill 1.0))
    def pad(x):
      shape = {'name': _convert_sexp_symbol_to_string(x[1]) }
      smd = (_convert_sexp_symbol_to_string(x[2]) == 'smd')
      if smd:
        shape['type'] = 'smd'
      else:
        shape['type'] = 'pad'
      s = _convert_sexp_symbol_to_string(x[3])
      [x1, y1, rot] = get_at_sub(x)
      shape['x'] = x1
      shape['y'] = -y1
      # TODO: Add rotated pad support
      shape['rot'] = rot
      [dx, dy] = get_sub(x, 'size')
      if s == 'circle':
        shape['shape'] = 'disc'
        shape['r'] = dx/2
      elif s == 'rect':
        shape['shape'] = 'rect'
        shape['dx'] = dx
        shape['dy'] = dy
      elif s == 'oval':
        shape['shape'] = 'rect'
        shape['dx'] = dx
        shape['dy'] = dy
        shape['ro'] = 100
      else:
        raise Exception("Pad with unknown shape %s" % (str(s)))
      if not smd:
        drill = get_sub(x, 'drill')
        shape['drill'] = drill[0]
        if has_sub(drill, 'offset'):
          [drill_dx, drill_dy] = get_sub(drill, 'offset')
          shape['drill_dx'] = drill_dx
          shape['drill_dy'] = -drill_dy
      return shape

    #(fp_line (start -2.54 -1.27) (end 2.54 -1.27) (layer F.SilkS) (width 0.381))
    def fp_line(x):
      [x1, y1] = get_sub(x, 'start')
      [x2, y2] = get_sub(x, 'end')
      layer = get_layer_sub(x, 'silk')
      width = get_single_element_sub(x, 'width')
      shape = { 
        'shape': 'line',
        'x1': x1, 'y1': -y1, 
        'x2': x2, 'y2': -y2, 
        'type': layer, 'w': width
      }
      return shape

    # (fp_circle (center 5.08 0) (end 6.35 -1.27) (layer F.SilkS) (width 0.15))
    def fp_circle(x):
      shape = { 'shape': 'circle' }
      [x1, y1] = get_sub(x, 'center')
      shape['x'] = x1
      shape['y'] = -y1
      shape['width'] = get_single_element_sub(x, 'width')
      [ex, ey] = get_sub(x, 'end')
      dx = abs(x1 - ex)
      dy = abs(y1 - ey)
      if f_eq(dx, dy):
        shape['r'] = dx*math.sqrt(2)
        if f_eq(shape['width'], shape['r']):
          shape['type'] = 'disc'
          shape['r'] = shape['r'] * 2
          del shape['width']
      else:
        shape['rx'] = dx*math.sqrt(2)
        shape['ry'] = dy*math.sqrt(2)
      shape['type'] = get_layer_sub(x, 'silk')
      return shape

    # (fp_arc (start 7.62 0) (end 7.62 -2.54) (angle 90) (layer F.SilkS) (width 0.15))
    def fp_arc(x):
      [x1, y1] = get_sub(x, 'start')
      [x2, y2] = get_sub(x, 'end')
      [a] = get_sub(x, 'angle')
      width = get_single_element_sub(x, 'width')
      shape = { 'shape': 'arc'}
      shape['type'] = get_layer_sub(x, 'silk')
      shape['a'] = a
      shape['x1'] = x1
      shape['y1'] = -y1
      shape['x2'] = x2
      shape['y2'] = -y2
      shape['w'] = width
      return shape

    # (fp_text reference MYCONN3 (at 0 -2.54) (layer F.SilkS)
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    # (fp_text value SMD (at 0 2.54) (layer F.SilkS) hide
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    def fp_text(x):
      shape = { 'shape': 'label', 'type': 'silk', 'value': '' }
      shape['value'] = _convert_sexp_symbol_to_string(x[2])
      shape['type'] = get_layer_sub(x, 'silk')
      
      if (_convert_sexp_symbol_to_string(x[1]) == "reference"):
        shape['value'] = 'NAME' # Override "NAME" field text
      elif (_convert_sexp_symbol_to_string(x[1]) == "value"):
        shape['value'] = 'VALUE' # Override "VALUE" field text
      else:
        # Don't let 'user' fields have 'NAME' or 'VALUE' as text
        if ((shape['value'] == 'NAME') or (shape['value'] == 'VALUE')):
          shape['value'] = "_%s_" % (shape['value'])
      
      [x1, y1, rot] = get_at_sub(x)
      font = get_sub(get_sub(x, 'effects'), 'font')
      [dx, dy] = get_sub(font, 'size')
      w = get_sub(font, 'thickness')
      shape['x'] = x1
      shape['y'] = -y1
      shape['w'] = w
      shape['dy'] = dy
      # TODO: Add rotated text support
      shape['rot'] = rot
      return shape

    for x in s[3:]:
      print "ELEMENT:"
      print x
      res = {
        'descr': descr,
        'pad': pad,
        'fp_line': fp_line,
        'fp_circle': fp_circle,
        'fp_arc': fp_arc,
        'fp_text': fp_text,
      }.get(_convert_sexp_symbol_to_string(x[0]), lambda a: None)(x)
      if res != None:
        l.append(res)
    return l

    
    
