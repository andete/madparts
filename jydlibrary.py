# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore

import jydjs

# get rid of copies from jydgldraw.py
def oget(m, k, d):
  if k in m: return m[k]
  return d

class Footprint():
  def __init__(self, parent, path, filename):
    self.parent = parent
    self.path = path
    self.filename = filename
 
  def load(self):
    with open(self.path) as f:
      code = f.read()
    shapes = jydjs.eval_coffee_footprint(code)
    for shape in shapes:
      if shape['type'] == 'meta':
        self.name = shape['name']
        self.id = shape['id']
        self.desc = oget(shape, 'desc', '')
    return self
 
  def draw(self):
    name_item = QtGui.QStandardItem(self.name)
    id_item   = QtGui.QStandardItem(self.id)
    desc_item = QtGui.QStandardItem(self.desc)
    name_item.setEditable(False) # you edit them in the code
    id_item.setEditable(False)
    desc_item.setEditable(False)
    self.parent.appendRow([name_item, id_item, desc_item])

class Library(QtGui.QStandardItem):

  def scan(self):
    self.removeRows(0, self.rowCount())
    d = QtCore.QDir(self.directory)
    self.footprints = []
    for f in d.entryList(['*.coffee']):
      path = d.filePath(f)
      try:
        foot = Footprint(self, path, f)
        self.footprints.append(foot)
        foot.load().draw()
      except Exception as ex:
        print "error for file %s:" % (path)
        traceback.print_exc()
    self.sortChildren(0)

  def __init__(self, name, directory):
    super(Library, self).__init__(name + " (" + directory + ")")
    self.name = name
    self.directory = directory
    self.setEditable(False)
    self.scan()
