# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path
import glob

import sexpdata
from sexpdata import Symbol as S

from mutil.mutil import *
from inter import inter

def type_to_layer_number(layer):
  type_to_layer_number_dict = {
    'smd': 'F.Cu', # these two are normally
    'pad': 'F.Cu', # not used like this
    'silk': 'F.SilkS',
    'name': 'F.SilkS',
    'value': 'Cmts.User',
    'stop': 'F.Mask',
    'glue': 'F.Adhes',
    'docu': 'Cmts.User',
    }
  return type_to_layer_number_dict[layer]

def detect(fn):
  if os.path.isdir(fn) and '.pretty' in fn:
    return True
  try:
    l = sexpdata.load(open(fn, 'r'))
    return l[0] == S('module')
  except IOError:
    # allow new .kicad_mod files!
    if '.kicad_mod' in fn: return True
    return False

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
      l.append([S('at'), fget(shape, 'x'), fget(shape, 'y'), iget(shape, 'rot')])
      if smd:
        l.append([S('layers'), S('F.Cu'), S('F.Paste'), S('F.Mask')])
      else:
        l.append([S('layers'), S('*.Cu'), S('*.Mask')]) # F.SilkS ?
      if not smd:
        l2 = [S('drill'), fget(shape, 'drill')]
        if 'drill_dx' in shape or 'drill_dy' in shape:
          l2.append([S('offset'), fget(shape, 'drill_dx'), fget(shape, 'drill_dy')])
        l.append(l2)
      return l
    
    #(fp_line (start -2.54 -1.27) (end 2.54 -1.27) (layer F.SilkS) (width 0.381))
    def line(shape, layer):
      l = [S('fp_line')] 
      l.append([S('start'), fget(shape, 'x1'), fget(shape, 'y1')])
      l.append([S('end'), fget(shape, 'x2'), fget(shape, 'y2')])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), fget(shape, 'w')])
      return l

    # (fp_circle (center 5.08 0) (end 6.35 -1.27) (layer F.SilkS) (width 0.15))
    def circle(shape, layer):
      l = [S('fp_circle')] 
      x = fget(shape, 'x')
      y = fget(shape, 'y')
      l.append([S('center'), x, y])
      r = fget(shape, 'r')
      l.append([S('end'), x+(r/sqrt(2)), y+(r/sqrt(2))])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), fget(shape, 'w')])
      return l

    # a disc is just a circle with a clever radius and width
    def disc(shape, layer):
      l = [S('fp_circle')] 
      x = fget(shape, 'x')
      y = fget(shape, 'y')
      l.append([S('center'), x, y])
      r = fget(shape, 'r')
      rad = r/2
      l.append([S('end'), x+(rad/sqrt(2)), y+(rad/sqrt(2))])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), rad])
      return l

    # (fp_arc (start 7.62 0) (end 7.62 -2.54) (angle 90) (layer F.SilkS) (width 0.15))
    def arc(shape, layer):
      l = [S('fp_arc')] 
      l.append([S('start'), fget(shape, 'x1'), fget(shape, 'y1')])
      l.append([S('end'), fget(shape, 'x2'), fget(shape, 'y2')])
      l.append([S('angle'), fget(shape, 'a')])
      l.append([S('layer'), S(layer)])
      l.append([S('w'), fget(shape, 'w')])
      return l


    # (pad "" smd rect (at 1.27 0) (size 0.39878 0.8001) (layers F.SilkS))
    def rect(shape, layer):
      l = [S('fp_arc'), ''. S('smd'), S('rect')] 
      l.append([S('at'), fget(shape, 'x'), fget(shape, 'y'), iget(shape, 'rot')])
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
      t = 'reference'
      if s == VALUE: t = 'value'
      l = [S('fp_text'), S(t), S(shape['value'])]
      l.append([S('at'), fget(shape, 'x'), fget(shape, 'y')])
      l.append([S('layer'), S(layer)])
      if s == 'VALUE':
        l.append(S('hide'))
      dy = fget(shape, 'dy', 1)
      th = fget(shape, 'w', 0.25)
      l.append([S('effects'), 
                [S('font'), [S('size'), dy, dy], [S('thickness'), w]]])
      return l

    def silk(shape):
      if not 'shape' in shape: return None
      layer = type_to_layer_number(shape['type'])
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

class Import:

  def __init__(self, fn):
    self.fn = fn

  def list(self):
    if os.path.isdir(self.fn) and '.pretty' in self.fn:
      files = glob.glob(self.fn + '/*.kicad_mod')
    else:
      files = [self.fn]
    for f in files:
      l = sexpdata.load(open(f, 'r'))
      print l[1].value()
