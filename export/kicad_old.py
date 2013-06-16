# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path

def detect(fn):
  if os.path.isdir(fn): return None
  try:
    with open(fn, 'r') as f:
      l = f.readlines()
      l0 = l[0]
      l2 = l0.split()
      if (l2[0] == 'PCBNEW-LibModule-V1'): return "1"
      elif (l2[0] == 'PCBNEW-LibModule-V2'): return "2"
      return None
  except:
    return None

class Import:

  def __init__(self, fn):
    self.fn = fn

  def list(self):
    with open(self.fn, 'r') as f:
      lines = f.readlines()
    for line in lines:
      if '$MODULE' in line:
        print line.split()[1]

class Export:

  def __init__(self, fn):
    self.fn = fn

  def export_footprint(self, interim):
    raise Exception("Export to KiCad old not yet supported")

  def save(self):
    pass
