# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import coffee.pycoffee as pycoffee
from util.util import *
from gui.dialogs import *

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
    _add('&Remove', self.remove_footprint)
    _add('&Clone', self.clone_footprint)
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

  def remove_footprint(self):
    directory = self.parent.lib[self.active_library].directory
    fn = self.active_footprint_id + '.coffee'
    QtCore.QDir(directory).remove(fn)
    # fall back to first_foot in library, if any
    library = self.rescan_library(self.active_library)
    if library.select_first_foot():
      self.active_footprint_id = library.first_foot_id
      self.active_library = library.name
    # else fall back to any first foot...
    else:
      root = self.model.invisibleRootItem()
      for row_index in range(0, root.rowCount()):
        library = root.child(row_index)
        if library.select_first_foot():
          self.active_footprint_id = library.first_foot.id
          self.active_library = library.name
    directory = self.parent.lib[self.active_library].directory
    fn = self.active_footprint_id + '.coffee'
    ffn = QtCore.QDir(directory).filePath(fn)
    with open(ffn) as f:
       self.parent.te1.setPlainText(f.read())
    # else... ?
    # TODO we don't support being completely footless now

  def clone_footprint(self):    
    if self.parent.executed_footprint == []:
      s = "Can't clone if footprint doesn't compile."
      QtGui.QMessageBox.warning(self, "warning", s)
      self.parent.status(s) 
      return
    old_code = self.parent.te1.toPlainText()
    old_meta = pycoffee.eval_coffee_meta(old_code)
    dialog = CloneFootprintDialog(self.parent, old_meta, old_code)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = pycoffee.clone_coffee_meta(old_code, old_meta, new_id, new_name)
    lib_dir = QtCore.QDir(self.parent.lib[new_lib].directory)
    new_file_name = lib_dir.filePath("%s.coffee" % (new_id))
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    s = "%s/%s cloned to %s/%s." % (self.active_library, old_meta['name'], new_lib, new_name)
    self.parent.te1.setPlainText(new_code)
    self.rescan_library(new_lib, new_id)
    self.active_footprint_id = new_id
    self.active_library = new_lib
    self.parent.show_footprint_tab()
    self.parent.status(s)

  def rescan_library(self, name, select_id = None):
    root = self.model.invisibleRootItem()
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.name == name:
        library.scan()
        if select_id is not None:
          library.select(select_id)
        self.expandAll()
        return library
    return None



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
