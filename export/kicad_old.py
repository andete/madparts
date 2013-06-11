# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path

def detect(fn):
  if os.path.isdir(fn): return False
  try:
    with open(fn, 'r') as f:
      l = f.readlines()
      l0 = l[0]
      l2 = l0.split()
      return l2[0] == 'PCBNEW-LibModule-V1'
  except:
    return False

class Import:

  def __init__(self, fn):
    self.fn = fn

  def list(self):
    with open(self.fn, 'r') as f:
      lines = f.readlines()
    for line in lines:
      if '$MODULE' in line:
        print line.split()[1]
