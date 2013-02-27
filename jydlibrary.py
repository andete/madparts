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
    self.identify = ('footprint', (self.lib_name, self.id))
    self.desc = oget(meta, 'desc', '')
    self.parent = oget(meta, 'parent', None)
 
  def add_to(self, parent):
    # print "adding %s to %s" % (self.name, parent.data(QtCore.Qt.UserRole))
    name_item = QtGui.QStandardItem(self.name)
    name_item.setData(self.identify, QtCore.Qt.UserRole)
    name_item.setToolTip(self.desc)
    id_item   = QtGui.QStandardItem(self.id)
    id_item.setData(self.identify, QtCore.Qt.UserRole)
    id_item.setToolTip(self.desc)
    name_item.setEditable(False) # you edit them in the code
    id_item.setEditable(False)
    parent.appendRow([name_item, id_item])
    self.item = name_item
    self.id_item = id_item

  def select(self, selection_model):
    print "%s/%s selected." % (self.lib_name, self.name)
    selection_model.select(self.item.index(), QtGui.QItemSelectionModel.ClearAndSelect)
    selection_model.select(self.id_item.index(), QtGui.QItemSelectionModel.Select)

class Library(QtGui.QStandardItem):

  def __init__(self, name, directory):
    super(Library, self).__init__(name)
    print "making %s" % (name)
    self.name = name
    self.setData(('library', name), QtCore.Qt.UserRole)
    self.directory = directory
    self.selected_foot = None
    self.setEditable(False)
    self.scan()

  def scan(self, select_id = None):
    self.selected_foot = None
    self.removeRows(0, self.rowCount())
    self.row_data = []
    self.footprints = []
    self.first_foot = None
    d = QtCore.QDir(self.directory)
    if not d.exists(): 
      self.setEnabled(False)
      return
    for f in d.entryList(['*.coffee']):
      path = d.filePath(f)
      try:
        foot = Footprint(self.name)
        foot.load(path)
        if foot.id == select_id:
          self.selected_foot = foot
        self.footprints.append(foot)
        self.row_data.append(path)
      except Exception as ex:
        print "error for file %s:" % (path)
        traceback.print_exc()
    if self.footprints == []: return # bail on an empty library
    # this algorithm isn't exactly nice
    # once libraries start getting bigger it should be improved
    foots_id = map(lambda fp: fp.id, self.footprints)
    def is_root_foot(fp):
      if fp.parent == None:
        return True
      if fp.parent in foots_id:
        return False
      return True
    root_foots = filter(is_root_foot , self.footprints)
    self.first_foot = root_foots[0]
    root_foots_id = map(lambda fp: fp.id, root_foots)
    foots_todo = filter(lambda fp: fp.id not in root_foots_id, self.footprints)
    for foot in root_foots:
      foot.add_to(self)
    while foots_todo != []:
      new_foot_todo = []
      for foot in foots_todo:
        if foot.parent in root_foots_id:
          i = root_foots_id.index(foot.parent)
          root_foots_id.append(foot.id)
          root_foots.append(foot)
          foot.add_to(root_foots[i].item) # 
        else:
          new_foot_todo.append(foot)
      foots_todo = new_foot_todo 
    self.sortChildren(0)

  def first_footprint(self):
    return self.first_foot
