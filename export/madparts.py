# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path
import glob

import coffee.library

def detect(fn):
  if not os.path.isdir(fn): return False
  return len(glob.glob(fn + '/*.coffee')) > 0

class Import:

  def __init__(self, fn):
    self.fn = fn


  def list(self):
    library = coffee.library.Library('library', self.fn)
    for meta in library.meta_list:
      print meta.id, meta.name
