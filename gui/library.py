# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import coffee.pycoffee as pycoffee
from util.util import *

class Library(QtGui.QStandardItem):

  def __init__(self, coffee_lib):
    self.coffee_lib = coffee_lib
    name = coffee_lib.name
    self.name = name
    super(Library, self).__init__(name)
    print "making %s" % (name)
    self.setData(('library', name), Qt.UserRole)
    self.directory = coffee_lib.directory
    self.selected_foot = None
    self.setEditable(False)
    self.items = {}
    self.id_items = {}
    self.scan()

  def select(self, selection_model, id):
    meta = self.coffee_lib.meta_by_id[id]
    print "%s/%s selected." % (meta.filename, meta.name)
    item = self.items[id]
    id_item = self.id_items[id]
    selection_model.select(item.index(), QtGui.QItemSelectionModel.ClearAndSelect)
    selection_model.select(id_item.index(), QtGui.QItemSelectionModel.Select)

  def append(self, meta):
    # print "adding %s to %s" % (self.name, parent.data(Qt.UserRole))
    name_item = QtGui.QStandardItem(meta.name)
    identify = ('footprint', (self.name, meta.id))
    name_item.setData(identify, Qt.UserRole)
    name_item.setToolTip(meta.desc)
    id_item   = QtGui.QStandardItem(meta.id)
    id_item.setData(identify, Qt.UserRole)
    id_item.setToolTip(meta.desc)
    name_item.setEditable(False) # you edit them in the code
    id_item.setEditable(False)
    if meta.readonly:
      name_item.setForeground(QtGui.QBrush(Qt.gray))
      id_item.setForeground(QtGui.QBrush(Qt.gray))
    self.appendRow([name_item, id_item])
    self.items[meta.id] = name_item
    self.id_items[meta.id] = id_item

  def scan(self, select_id = None):
    self.selected_foot = None
    self.removeRows(0, self.rowCount())
    self.row_data = []
    self.footprints = []
    self.first_foot_id = None
    if not self.coffee_lib.exists:
      self.setForeground(QtGui.QBrush(Qt.red))
      return

    def _add(meta_list):
      if meta_list == []: return
      for meta in meta_list:
        self.append(meta)
        _add(map(lambda id: self.coffee_lib.meta_by_id[id], meta.child_ids))
       
    _add(self.coffee_lib.root_meta_list)
    if self.coffee_lib.root_meta_list != []:
      self.first_foot_id = self.coffee_lib.root_meta_list[0].id
