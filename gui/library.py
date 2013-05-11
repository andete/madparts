# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import coffee.pycoffee as pycoffee
from util.util import *

class LibraryTree(QtGui.QTreeView):

  def __init__(self, parent):
    super(LibraryTree, self).__init__()
    self.parent = parent
    self.active_footprint_id = None
    self.active_library = None
    self._populate()

  def active_footprint_file(self):
   dir = QtCore.QDir(self.parent.lib[self.active_library].directory)
   return dir.filePath(self.active_footprint_id + '.coffee')

  def _make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(2)
    self.model.setHorizontalHeaderLabels(['name','id'])
    parentItem = self.model.invisibleRootItem()
    first = True
    first_foot_id = None
    first_foot_lib = None
    for coffee_lib in self.parent.lib.values():
      guilib = Library(self.selectionModel, coffee_lib)
      parentItem.appendRow(guilib)
      if first:
        first_foot_id = guilib.first_foot_id
        first_foot_lib = guilib
        first = first_foot_id is None
    return (first_foot_lib, first_foot_id)

  def _populate(self):
    (first_foot_lib, first_foot_id) = self._make_model()
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    self.setModel(self.model)
    self.selectionModel().currentRowChanged.connect(self.parent.row_changed)
    self.setRootIsDecorated(False)
    self.expandAll()
    self.setItemsExpandable(False)
    self.resizeColumnToContents(0)
    self.doubleClicked.connect(self.parent.show_footprint_tab)
    self.active_footprint_id = None
    self.active_library = None
    if first_foot_lib is not None:
      print "selected", first_foot_lib.name
      if first_foot_lib.select_first_foot():
        print "selected", first_foot_id
        self.active_footprint_id = first_foot_id
        self.active_library = first_foot_lib.name
    self._footprint_selected()

  def _footprint_selected(self):
    for action in self.actions():
      self.removeAction(action)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self)
      self.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Remove', self.parent.remove_footprint)
    _add('&Clone', self.parent.clone_footprint)
    _add('&Move', self.parent.move_footprint)
    _add('&Export previous', self.parent.export_previous)
    _add('E&xport', self.parent.export_footprint)
    _add('&Print')
    _add('&Reload', self.parent.reload_footprint)

  def _library_selected(self):
    for action in self.actions():
      self.removeAction(action)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self)
      self.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Disconnect', self.parent.disconnect_library)
    _add('&Import', self.parent.import_footprints)
    _add('&Reload', self.parent.reload_library)
    _add('&New', self.parent.new_footprint)


class Library(QtGui.QStandardItem):

  def __init__(self, selection_model, coffee_lib):
    self.selection_model = selection_model
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
    self.first_foot_id = None
    self.scan()

  def select(self, id):
    meta = self.coffee_lib.meta_by_id[id]
    print "%s/%s selected." % (meta.filename, meta.name)
    item = self.items[id]
    id_item = self.id_items[id]
    self.selection_model().select(item.index(), QtGui.QItemSelectionModel.ClearAndSelect)
    self.selection_model().select(id_item.index(), QtGui.QItemSelectionModel.Select)

  def select_first_foot(self):
    if self.first_foot_id is not None:
      self.select(self.first_foot_id)
      return True
    return False

  def append(self, parent, meta):
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
    parent.appendRow([name_item, id_item])
    self.items[meta.id] = name_item
    self.id_items[meta.id] = id_item
    return name_item

  def scan(self):
    self.coffee_lib.scan()
    self.items = {}
    self.id_items = {}
    self.selected_foot = None
    self.removeRows(0, self.rowCount())
    self.row_data = []
    self.footprints = []
    self.first_foot_id = None
    if not self.coffee_lib.exists:
      self.setForeground(QtGui.QBrush(Qt.red))
      return

    def _add(parent, meta_list):
      if meta_list == []: return
      for meta in meta_list:
        new_item = self.append(parent, meta)
        _add(new_item, map(lambda id: self.coffee_lib.meta_by_id[id], meta.child_ids))
       
    _add(self, self.coffee_lib.root_meta_list)
    if self.coffee_lib.root_meta_list != []:
      self.first_foot_id = self.coffee_lib.root_meta_list[0].id
