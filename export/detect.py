# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import eagle, kicad, madparts, kicad_old

MADPARTS = "madparts"
EAGLE = "eagle"
KICAD = "kicad"
KICAD_OLD = "kicad-old"

def detect(fn):
  v =  madparts.detect(fn)
  if v is not None:
    return (MADPARTS, v)
  v = eagle.detect(fn)
  if v is not None:
    return (EAGLE, v)
  v = kicad.detect(fn)
  if v is not None:
    return (KICAD, v)
  v = kicad_old.detect(fn)
  if v is not None:
    return (KICAD_OLD, v)
  raise Exception("Unknown file format")

def make_exporter(fn):
  (t,_) = detect(fn)
  if t == EAGLE:
    return eagle.Export(fn)
  elif t == KICAD:
    return kicad.Export(fn)
  elif t == KICAD_OLD:
    return kicad_old.Export(fn)
  else:
    raise Exception("Invalid export format")

def make_importer(fn):  
  (t,_) = detect(fn)
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
