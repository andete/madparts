# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path
import glob

import sexpdata
from sexpdata import Symbol as S

def detect(fn):
  if os.path.isdir(fn) and '.pretty' in fn:
    return True
  try:
    l = sexpdata.load(open(fn, 'r'))
    return l[0] == S('module')
  except:
    return False

class Export:

  def __init__(self, fn):
    self.fn = fn
    # maybe need to load the file, depending on
    # the type of file, if it is a .kicad_mod file
    # it contains only one footprint and can just be
    # written from scratch
    # this is what will be supported as a first step

  def export_footprint(self, interim):
    name = eget(meta, 'name', 'Name not found')
    idx = eget(meta, 'id', 'Id not found')
    desc = oget(meta, 'desc', '')
    parent_idx = oget(meta, 'parent', None)
    l = [
      S('module'),
      S(name),
      [S('layer'), S('F.Cu')],
      [S('desc'), desc],
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
        l.append([S('size'), r, r, fget(shape, 'rot')])
      elif shape2 == 'rect':
        ro = iget(shape, 'ro')
        if ro == 0:
          l.append(S('rect'))
        else:
          l.append(S('oval'))
        l.append([S('size'), fget(shape, 'dx'), fget(shape, 'dy'), fget(shape, 'rot')])
      else:
        raise Exception("%s shaped pad not supported in kicad" % (shape2))
      l.append([S('at'), fget(shape, 'x'), fget(shape, 'y'), iget(shape, 'ro')])
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
    with open(self.fn, 'w+') as f:
      sexpdata.dump(l, f)
    return name

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
