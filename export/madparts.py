# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path

import coffee.library

def detect(fn):
  # TODO better detection of madparts library!
  return os.path.isdir(fn)

class Import:

  def __init__(self, fn):
    self.fn = fn


  def list(self):
    library = coffee.library.Library('library', self.fn)
    for meta in library.meta_list:
      print meta.id, meta.name
