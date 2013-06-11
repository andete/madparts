# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import eagle, kicad, madparts

MADPARTS = 0
EAGLE = 1
KICAD = 2

def detect(fn):
  if madparts.detect(fn):
    return MADPARTS
  elif eagle.detect(fn):
    return EAGLE
  elif kicad.detect(fn):
    return kicad
  else:
    raise Exception("Unknown file format")

def make_exporter(fn):
  t = detect(fn)
  if t == EAGLE:
    return eagle.Export(fn)
  elif t == KICAD:
    return kicad.Export(fn)
  else:
    raise Exception("Invalid export format")

def make_importer(fn):  
  t = detect(fn)
  if t == EAGLE:
    return eagle.Import(fn)
  elif t == KICAD:
    return kicad.Import(fn)
  elif t == MADPARTS:
    return madparts.Import(fn) # for listing!
  else:
    raise Exception("Invalid export format")
