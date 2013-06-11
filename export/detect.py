# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import eagle, kicad, madparts, kicad_old

MADPARTS = 0
EAGLE = 1
KICAD = 2
KICAD_OLD = 3

def detect(fn):
  if madparts.detect(fn):
    return MADPARTS
  elif eagle.detect(fn):
    return EAGLE
  elif kicad.detect(fn):
    return KICAD
  elif kicad_old.detect(fn):
    return KICAD_OLD
  else:
    raise Exception("Unknown file format")

def make_exporter(fn):
  t = detect(fn)
  if t == EAGLE:
    return eagle.Export(fn)
  elif t == KICAD:
    return kicad.Export(fn)
  elif t == KICAD_OLD:
    return kicad_old.Export(fn)
  else:
    raise Exception("Invalid export format")

def make_importer(fn):  
  t = detect(fn)
  if t == EAGLE:
    return eagle.Import(fn)
  elif t == KICAD:
    return kicad.Import(fn)
  elif t == KICAD_OLD:
    return kicad_old.Import(fn)
  elif t == MADPARTS:
    return madparts.Import(fn) # for listing!
  else:
    raise Exception("Invalid export format")
