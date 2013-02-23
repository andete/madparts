# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore

import jydcoffee
from jydutil import *

class Footprint():
  def __init__(self, lib_name):
    self.lib_name = lib_name
 
  def load(self, path):
    with open(path) as f:
      code = f.read()
    meta = jydcoffee.eval_coffee_meta(code)
    self.name = meta['name']
    self.id = meta['id']
    self.identify = (self.lib_name, self.id)
    self.desc = oget(meta, 'desc', '')
    self.parent = oget(meta, 'parent', None)
    return self
 
  def draw(self, parent):
    name_item = QtGui.QStandardItem(self.name)
    name_item.setData(self.identify, QtCore.Qt.UserRole)
    id_item   = QtGui.QStandardItem(self.id)
    id_item.setData(self.identify, QtCore.Qt.UserRole)
    desc_item = QtGui.QStandardItem(self.desc)
    desc_item.setData(self.identify, QtCore.Qt.UserRole)
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

  def __init__(self, name, directory):
    super(Library, self).__init__(name)
    self.name = name
    self.directory = directory
    self.setEditable(False)
    self.scan()

  def scan(self):
    self.removeRows(0, self.rowCount())
    self.row_data = []
    d = QtCore.QDir(self.directory)
    self.footprints = []
    for f in d.entryList(['*.coffee']):
      path = d.filePath(f)
      try:
        foot = Footprint(self.name)
        foot.load(path)
        self.footprints.append(foot)
        self.row_data.append(path)
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

  def first_footprint(self):
    return self.first_foot
