# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path
import glob

import sexpdata
from sexpdata import Symbol as S

from mutil.mutil import *
from inter import inter

def detect(fn):
  if os.path.isdir(fn) and '.pretty' in fn:
    return True
  try:
    l = sexpdata.load(open(fn, 'r'))
    return l[0] == S('module')
  except:
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
    
    def silk(shape):
      pass

    def unknown(shape):
      pass

    for shape in interim:
      if 'type' in shape:
        l2 = {
          'pad': pad,
          'silk': silk,
          'docu': silk,
          'keepout': silk,
          'stop': silk,
          'restrict': silk,
          'vrestrict': silk,
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
