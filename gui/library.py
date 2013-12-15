# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import traceback

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import coffee.pycoffee as pycoffee
import coffee.library
from mutil.mutil import *
from gui.dialogs import *
import sys, os

class Explorer(QtGui.QTreeView):

  def __init__(self, parent):
    super(Explorer, self).__init__()
    self.parent = parent
    self.coffee_lib = {}
    self.active_footprint = None
    self.active_library = None
    self.selected_library = None

  def has_footprint(self):
    return self.active_footprint is not None

  def initialize_libraries(self, settings):

    def load_libraries():
      size = settings.beginReadArray('library')
      for i in range(size):
        settings.setArrayIndex(i)
        name = settings.value('name')
        filen = settings.value('file')
        library = coffee.library.Library(name, filen)
        self.coffee_lib[name] = library
      settings.endArray()

    if not 'library' in settings.childGroups():
      if sys.platform == 'darwin':
        # TODO: retest and modify under darwin
        example_lib = QtCore.QDir('share/madparts/examples').absolutePath()
      else:
        data_dir = os.environ['DATA_DIR']
        
        example_lib = QtCore.QDir(os.path.join(data_dir, 'examples')).absolutePath()
      library = coffee.library.Library('Examples', example_lib)
      self.coffee_lib = { 'Examples': library }
      self.save_libraries(settings)
    else:
      self.coffee_lib = {}
      load_libraries()

  def save_libraries(self, settings):
    l = self.coffee_lib.values()
    settings.beginWriteArray('library')
    for i in range(len(l)):
      settings.setArrayIndex(i)
      settings.setValue('name', l[i].name)
      settings.setValue('file', l[i].directory)
    settings.endArray()

  def active_footprint_file(self):
   if self.active_footprint is None: return None
   return self.active_footprint.filename

  def _selection_model(self):
    return self.selection_model

  def _make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.selection_model = QtGui.QItemSelectionModel(self.model, self)
    self.model.setColumnCount(2)
    self.model.setHorizontalHeaderLabels(['name','id'])
    parentItem = self.model.invisibleRootItem()
    first = True
    first_foot_meta = None
    first_foot_lib = None
    for coffee_lib in self.coffee_lib.values():
      guilib = Library(self._selection_model, coffee_lib)
      parentItem.appendRow(guilib)
      if first:
        first_foot_meta = guilib.first_foot_meta
        first_foot_lib = guilib
        first = first_foot_meta is None
    return (first_foot_lib, first_foot_meta)

  def populate(self):
    (first_foot_lib, first_foot_meta) = self._make_model()
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    self.setModel(self.model)
    self.setSelectionModel(self.selection_model)
    self._selection_model().currentRowChanged.connect(self.row_changed)
    self.setRootIsDecorated(False)
    self.expandAll()
    self.setItemsExpandable(False)
    self.resizeColumnToContents(0)
    self.doubleClicked.connect(self.parent.show_footprint_tab)
    self.active_footprint = None
    self.active_library = None
    if first_foot_lib is not None:
      #print "selected", first_foot_lib.name
#      if first_foot_lib.select_first_foot():
        #print "selected", first_foot_meta.id
        self.active_footprint = first_foot_meta
        self.active_library = first_foot_lib.coffee_lib
        self._footprint_selected()

  def row_changed(self, current, previous):
    x = current.data(QtCore.Qt.UserRole)
    if x == None: return
    (t,x) = x
    if t == 'library':
      self.selected_library = x
      self._library_selected()
      return
    # it is a footprint
    self.selected_library = None
    (lib_name, fpid) = x
    directory = self.coffee_lib[lib_name].directory
    meta = self.coffee_lib[lib_name].meta_by_id[fpid]
    fn = meta.filename
    #ffn = QtCore.QDir(directory).filePath(fn)
    self.active_footprint = meta
    self.active_library = self.coffee_lib[lib_name]
    self._footprint_selected()
    with open(fn) as f:
      self.parent.update_text(f.read())
    #self.parent.set_code_textedit_readonly(meta.readonly)


  def _footprint_selected(self):
    for action in self.actions():
      self.removeAction(action)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self)
      self.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    if self.active_library.readonly:
      _add('&Remove')
    else:
      _add('&Remove', self.remove_footprint)
    _add('&Clone', self.clone_footprint)
    _add('&Move', self.move_footprint)
    _add('&Export previous', self.parent.export_previous)
    _add('E&xport', self.parent.export_footprint)
    _add('&Print')
    _add('&Reload', self.parent.reload_footprint)
    self.parent.set_library_readonly(self.active_library.readonly)

  def _library_selected(self):
    for action in self.actions():
      self.removeAction(action)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self)
      self.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Disconnect', self.disconnect_library)
    lib = self.coffee_lib[self.selected_library]
    if lib.readonly or not lib.exists:
      _add('&Import')
      _add('&New')
    else:
      _add('&Import', self.parent.import_footprints)
      _add('&New', self.new_footprint)
    _add('&Reload', self.reload_library)
    self.parent.set_library_readonly(lib.readonly or not lib.exists)

  def remove_footprint(self):
    directory = self.active_library.directory
    fn = self.active_footprint.filename
    QtCore.QDir(directory).remove(fn)
    # fall back to first_foot in library, if any
    library = self.rescan_library(self.active_library.name)
    if library.select_first_foot():
      self.active_footprint = library.first_foot_meta
      self.active_library = library.coffee_lib
    # else fall back to any first foot...
    else:
      root = self.model.invisibleRootItem()
      for row_index in range(0, root.rowCount()):
        library = root.child(row_index)
        if library.select_first_foot():
          self.active_footprint_id = library.first_foot.id
          self.active_library = library
    directory = self.active_library.directory
    fn = self.active_footprint.id + '.coffee'
    ffn = QtCore.QDir(directory).filePath(fn)
    with open(ffn) as f:
       self.parent.update_text(f.read())
    # else... ?
    # TODO we don't support being completely footless now

  def clone_footprint(self):    
    if self.parent.executed_footprint == []:
      s = "Can't clone if footprint doesn't compile."
      QtGui.QMessageBox.warning(self, "warning", s)
      self.parent.status(s) 
      return
    old_code = self.parent.code_textedit.toPlainText()
    old_meta = pycoffee.eval_coffee_meta(old_code)
    dialog = CloneFootprintDialog(self, old_meta, old_code)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = pycoffee.clone_coffee_meta(old_code, old_meta, new_id, new_name)
    lib_dir = QtCore.QDir(self.coffee_lib[new_lib].directory)
    new_file_name = lib_dir.filePath("%s.coffee" % (new_id))
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    s = "%s/%s cloned to %s/%s." % (self.active_library.name, old_meta['name'], new_lib, new_name)
    self.active_library = self.rescan_library(new_lib, new_id)
    self.active_footprint = self.active_library.meta_by_id(new_id)
    self.parent.update_text(new_code)
    self.parent.show_footprint_tab()
    self.parent.status(s)

  def new_footprint(self):
    dialog = NewFootprintDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = pycoffee.new_coffee(new_id, new_name)
    lib_dir = QtCore.QDir(self.coffee_lib[new_lib].directory)
    new_file_name = lib_dir.filePath("%s.coffee" % (new_id))
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    self.parent.update_text(new_code)
    self.active_library = self.rescan_library(new_lib, new_id)
    self.active_footprint = self.active_library.meta_by_id(new_id)
    self.parent.show_footprint_tab()
    self.parent.status("%s/%s created." % (new_lib, new_name))

  def move_footprint(self):
    old_code = self.parent.code_textedit.toPlainText()
    old_meta = pycoffee.eval_coffee_meta(old_code)
    dialog = MoveFootprintDialog(self, old_meta)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_name, new_lib) = dialog.get_data()
    old_name = old_meta['name']
    my_id = self.active_footprint.id
    fn = my_id + '.coffee'
    old_lib = self.active_library
    new_code = old_code.replace("#name %s" % (old_name), "#name %s" % (new_name))
    new_lib_dir = QtCore.QDir(self.coffee_lib[new_lib].directory)
    new_file_name = new_lib_dir.filePath(fn)
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    status_str = "moved %s/%s to %s/%s." % (old_lib.name, old_name, new_lib, new_name)
    self.parent.status(status_str)
    if old_lib.name == new_lib: 
      self.rescan_library(old_lib.name, my_id) # just to update the nameq
    else:
      full_fn = os.path.join(old_lib.directory, fn)
      os.unlink(full_fn)
      self.rescan_library(old_lib.name)
      self.active_library = self.rescan_library(new_lib, my_id)

  def add_library(self):
    dialog = AddLibraryDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (name, directory) = dialog.get_data()
    lib = coffee.library.Library(name, directory)
    self.coffee_lib[name] = lib
    self.save_libraries(self.parent.settings)
    root = self.model.invisibleRootItem()
    guilib = Library(self.selectionModel, lib)
    root.appendRow(guilib)
    self.expandAll()  

  def disconnect_library(self):
    dialog = DisconnectLibraryDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    lib_name = dialog.get_data()
    del self.coffee_lib[lib_name]
    self.save_libraries(self.parent.settings)
    root = self.model.invisibleRootItem()
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.name == lib_name: break
    root.removeRow(row_index)
    if lib_name != self.active_library: return
    # select first foot of the first library which contains foots
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.select_first_foot():
        self.active_footprint = library.first_foot_meta
        self.active_library = library.coffee_lib
        fn = self.active_footprint.filename
        with open(fn) as f:
          self.parent.update_text(f.read())
        return

  def rescan_library(self, name, select_id = None):
    root = self.model.invisibleRootItem()
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.name == name:
        library.scan()
        if select_id is not None:
          select_meta = self.coffee_lib[name].meta_by_id[select_id]
          library.select(select_meta)
        self.expandAll()
        return library
    return None

  def reload_library(self):
    if self.selected_library != None:
      lib = self.selected_library
    else:
      lib = self.active_library.name
    self.rescan_library(lib)
    self.parent.status("%s reloaded." % (lib))


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
    self.first_foot_meta = None
    self.scan()

  def meta_by_id(self, id):
    return self.coffee_lib.meta_by_id[id]

  def select(self, meta):
    id = meta.id
    print "%s/%s selected." % (meta.filename, meta.name)
    item = self.items[id]
    id_item = self.id_items[id]
    self.selection_model().select(item.index(), QtGui.QItemSelectionModel.ClearAndSelect)
    self.selection_model().select(id_item.index(), QtGui.QItemSelectionModel.Select)

  def select_first_foot(self):
    if self.first_foot_meta is not None:
      self.select(self.first_foot_meta)
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
    self.first_foot_meta = None
    if not self.coffee_lib.exists:
      self.setForeground(QtGui.QBrush(Qt.red))
      return
    if self.coffee_lib.readonly:
      self.setForeground(QtGui.QBrush(Qt.gray))

    def _add(parent, meta_list):
      if meta_list == []: return
      for meta in meta_list:
        new_item = self.append(parent, meta)
        _add(new_item, map(lambda id: self.coffee_lib.meta_by_id[id], meta.child_ids))
       
    _add(self, self.coffee_lib.root_meta_list)
    if self.coffee_lib.root_meta_list != []:
      self.first_foot_meta = self.coffee_lib.root_meta_list[0]
