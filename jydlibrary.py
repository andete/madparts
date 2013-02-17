# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore

import jydcoffee

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
    meta = jydcoffee.eval_coffee_meta(code)
    self.name = meta['name']
    self.id = meta['id']
    self.desc = oget(meta, 'desc', '')
    self.parent = oget(meta, 'parent', None)
    return self
 
  # we use the EditRole to store the path so we immediately get the path on click
  # in any of the fields
  def draw(self, parent):
    name_item = QtGui.QStandardItem(self.name)
    name_item.setData(self.path, QtCore.Qt.EditRole)
    id_item   = QtGui.QStandardItem(self.id)
    id_item.setData(self.path, QtCore.Qt.EditRole)
    desc_item = QtGui.QStandardItem(self.desc)
    desc_item.setData(self.path, QtCore.Qt.EditRole)
    name_item.setEditable(False) # you edit them in the code
    id_item.setEditable(False)
    desc_item.setEditable(False)
    parent.appendRow([name_item, id_item, desc_item])
    self.item = name_item
    self.items = [id_item, desc_item]

  def select(self, selection_model):
    selection_model.select(self.item.index(), QtGui.QItemSelectionModel.ClearAndSelect)
    for item in self.items:
      selection_model.select(item.index(), QtGui.QItemSelectionModel.Select)

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
    # this algorithm isn't exactly nice
    # once libraries start getting bigger it should be improved
    foots_id = map(lambda fp: fp.id, self.footprints)
    def is_root_foot(fp):
      if fp.parent == None:
        return True
      if fp.parent in foots_id:
        return False
      return True
    foots_done = filter(is_root_foot , self.footprints)
    self.first_foot = foots_done[0]
    foots_done_id = map(lambda fp: fp.id, foots_done)
    foots_todo = filter(lambda fp: not is_root_foot(fp), self.footprints)
    for foot in foots_done:
      foot.draw(self)
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

  def first_footprint(self):
    return self.first_foot
