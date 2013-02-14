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
  def __init__(self, path, filename):
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
        self.parent = oget(shape, 'parent', None)
    return self
 
  def draw(self, parent):
    name_item = QtGui.QStandardItem(self.name)
    id_item   = QtGui.QStandardItem(self.id)
    desc_item = QtGui.QStandardItem(self.desc)
    name_item.setEditable(False) # you edit them in the code
    id_item.setEditable(False)
    desc_item.setEditable(False)
    parent.appendRow([name_item, id_item, desc_item])
    self.item = name_item

class Library(QtGui.QStandardItem):

  def scan(self):
    self.removeRows(0, self.rowCount())
    d = QtCore.QDir(self.directory)
    self.footprints = []
    for f in d.entryList(['*.coffee']):
      path = d.filePath(f)
      try:
        foot = Footprint(path, f)
        foot.load()
        self.footprints.append(foot)
      except Exception as ex:
        print "error for file %s:" % (path)
        traceback.print_exc()
    foots_done = filter(lambda fp: fp.parent == None , self.footprints)
    foots_done_id = map(lambda fp: fp.id, foots_done)
    foots_todo = filter(lambda fp: fp.parent != None, self.footprints)
    for foot in foots_done:
      foot.draw(self)
    # this algorithm doesn't halt when there is a reference to a
    # non-existing parent... TODO fix
    while foots_todo != []:
      new_foot_todo = []
      for foot in foots_todo:
        if foot.parent in foots_done_id:
          i = foots_done_id.index(foot.parent)
          foots_done_id.append(foot.id)
          foots_done.append(foot)
          foot.draw(foots_done[i].item)
        else:
          new_foot_todo.append(foot)
      foots_todo = new_foot_todo 
    self.sortChildren(0)

  def __init__(self, name, directory):
    super(Library, self).__init__(name)
    self.name = name
    self.directory = directory
    self.setEditable(False)
    self.scan()
