#!/opt/local/bin/python2.7
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import numpy as np
import math, time, traceback, re, os, os.path, sys

from PySide import QtGui, QtCore

from gui.dialogs import *
import gui.gldraw, gui.library

import coffee.pycoffee as pycoffee
import coffee.generatesimple as generatesimple

from inter import inter

from syntax.jssyntax import JSHighlighter
from syntax.coffeesyntax import CoffeeHighlighter

import export.eagle

class MainWin(QtGui.QMainWindow):

  def __init__(self):
    super(MainWin, self).__init__()

    self.settings = QtCore.QSettings()
    if not 'library' in self.settings.childGroups():
      if sys.platform == 'darwin':
        example_lib = QtCore.QDir('share/madparts/examples').absolutePath()
      else:
        example_lib = QtCore.QDir('examples').absolutePath()
      self.lib_dir = {'Examples':example_lib}
      self.lib_exist = {'Examples':True}
      self.save_libraries()
    else:
      self.lib_dir = {}
      self.lib_exist = {}
      self.load_libraries()

    splitter = QtGui.QSplitter(self, QtCore.Qt.Horizontal)
    splitter.addWidget(self._left_part())
    splitter.addWidget(self._right_part())
    self.setCentralWidget(splitter)

    self.statusBar().showMessage("Ready.")

    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    self.add_action(fileMenu, '&Quit', self.close, 'Ctrl+Q')

    editMenu = menuBar.addMenu('&Edit')
    self.add_action(editMenu, '&Preferences', self.preferences)

    footprintMenu = menuBar.addMenu('&Footprint')
    self.add_action(footprintMenu, '&Clone', self.clone_footprint, 'Ctrl+Alt+C')
    self.add_action(footprintMenu, '&Delete', self.remove_footprint, 'Ctrl+Alt+D')
    self.add_action(footprintMenu, '&New', self.new_footprint, 'Ctrl+Alt+N')
    self.add_action(footprintMenu, '&Move', self.move_footprint, 'Ctrl+Alt+M')
    self.add_action(footprintMenu, '&Export previous', self.export_previous, 'Ctrl+E')
    self.add_action(footprintMenu, '&Export', self.export_footprint, 'Ctrl+Alt+X')
    self.add_action(footprintMenu, '&Print', None, 'Ctrl+P')
    self.add_action(footprintMenu, '&Reload', self.reload_footprint, 'Ctrl+R')
    footprintMenu.addSeparator()

    self.display_docu = self.setting('gui/displaydocu') == 'True'
    self.display_restrict = self.setting('gui/displayrestrict') == 'True'
    self.display_stop = self.setting('gui/displaystop') == 'True'
    self.docu_action = self.add_action(footprintMenu, "&Display Docu", self.docu_changed, checkable=True, checked=self.display_docu)
    self.restrict_action = self.add_action(footprintMenu, "&Display Restrict", self.restrict_changed, checkable=True, checked=self.display_restrict)
    self.stop_action = self.add_action(footprintMenu, "&Display Stop", self.stop_changed, checkable=True, checked=self.display_stop)

    libraryMenu = menuBar.addMenu('&Library')
    self.add_action(libraryMenu, '&Add', self.add_library)
    self.add_action(libraryMenu, '&Disconnect', self.disconnect_library)
    self.add_action(libraryMenu, '&Import', self.import_footprints, 'Ctrl+Alt+I')
    self.add_action(libraryMenu, '&Reload', self.reload_library, 'Ctrl+Alt+R')

    helpMenu = menuBar.addMenu('&Help')
    self.add_action(helpMenu, '&About', self.about)

    self.last_time = time.time() - 10.0
    self.first_keypress = False
    self.timer = QtCore.QTimer()
    self.timer.setSingleShot(True)
    self.timer.timeout.connect(self.editor_text_changed)

    self.executed_footprint = []
    self.export_library_filename = ""
    self.export_library_filetype = ""
    self.is_fresh_from_file = True
    self.selected_library = None
    self.gl_dx = 0
    self.gl_dy = 0
    self.gl_w = 0
    self.gl_h = 0

  ### GUI HELPERS

  def _make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(2)
    self.model.setHorizontalHeaderLabels(['name','id'])
    parentItem = self.model.invisibleRootItem()
    first = True
    for (name, directory) in self.lib_dir.items():
      lib = gui.library.Library(name, directory)
      parentItem.appendRow(lib)
      if first:
        first_foot = lib.first_footprint()
        first = first_foot == None
    return first_foot

  def _tree(self):
    first_foot = self._make_model()
    tree = QtGui.QTreeView()
    tree.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    tree.setModel(self.model)
    tree.setRootIsDecorated(False)
    tree.expandAll()
    tree.setItemsExpandable(False)
    tree.resizeColumnToContents(0)
    self.tree_selection_model = tree.selectionModel()
    self.tree_selection_model.currentRowChanged.connect(self.row_changed)
    tree.doubleClicked.connect(self.show_footprint_tab)
    first_foot.select(self.tree_selection_model)
    self.tree = tree
    self._tree_footprint_selected()
    self.active_footprint_id = first_foot.id
    self.active_library = first_foot.lib_name
    return tree

  def _tree_footprint_selected(self):
    for action in self.tree.actions():
      self.tree.removeAction(action)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self.tree)
      self.tree.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Remove', self.remove_footprint)
    _add('&Clone', self.clone_footprint)
    _add('&Move', self.move_footprint)
    _add('&Export previous', self.export_previous)
    _add('E&xport', self.export_footprint)
    _add('&Print')
    _add('&Reload', self.reload_footprint)

  def _tree_library_selected(self):
    for action in self.tree.actions():
      self.tree.removeAction(action)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self.tree)
      self.tree.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Disconnect', self.disconnect_library)
    _add('&Import', self.import_footprints)
    _add('&Reload', self.reload_library)
    _add('&New', self.new_footprint)

  def _footprint(self):
    lsplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
    self.te1 = QtGui.QTextEdit()
    self.te1.setAcceptRichText(False)
    with open(self.active_footprint_file()) as f:
        self.te1.setPlainText(f.read())
    self.highlighter1 = CoffeeHighlighter(self.te1.document())
    self.te1.textChanged.connect(self.editor_text_changed)
    self.te2 = QtGui.QTextEdit()
    self.te2.setReadOnly(True)
    self.highlighter2 = JSHighlighter(self.te2.document())
    lsplitter.addWidget(self.te1)
    lsplitter.addWidget(self.te2)
    self.lsplitter = lsplitter
    [s1, s2] = lsplitter.sizes()
    lsplitter.setSizes([min(s1+s2-150, 150), 150])
    return lsplitter  

  def _left_part(self):
    lqtab = QtGui.QTabWidget()
    lqtab.addTab(self._tree(), "library")
    lqtab.addTab(self._footprint(), "footprint")
    lqtab.setCurrentIndex(1)
    self.left_qtab = lqtab
    return lqtab

  def _right_part(self):
    rvbox = QtGui.QVBoxLayout()
    rhbox = QtGui.QHBoxLayout()
    self.glw = gui.gldraw.JYDGLWidget(self)
    self.zoom_selector = QtGui.QLineEdit(str(self.glw.zoomfactor))
    self.zoom_selector.setValidator(QtGui.QIntValidator(1, 250))
    self.zoom_selector.editingFinished.connect(self.zoom)
    self.zoom_selector.returnPressed.connect(self.zoom)
    rhbox.addWidget(QtGui.QLabel("Zoom: "))
    rhbox.addWidget(self.zoom_selector)
    self.auto_zoom = QtGui.QCheckBox("Auto")
    self.auto_zoom.setChecked(bool(self.setting('gl/autozoom')))
    self.auto_zoom.stateChanged.connect(self.zoom)
    self.auto_zoom.stateChanged.connect(self.auto_zoom_changed)
    rhbox.addWidget(self.auto_zoom)
    rvbox.addLayout(rhbox)
    rvbox.addWidget(self.glw)

    right = QtGui.QWidget(self)
    right.setLayout(rvbox)
    return right

  def about(self):
    a = """
<p align="center"><b>madparts</b><br/>the functional footprint editor</p>
<p align="center">(c) 2013 Joost Yervante Damad &lt;joost@damad.be&gt;</p>
<p align="center"><a href="http://madparts.org">http://madparts.org</a></p>
"""
    QtGui.QMessageBox.about(self, "about madparts", a)

  def add_action(self, menu, text, slot, shortcut=None, checkable=False, checked=False):
    action = QtGui.QAction(text, self)
    if checkable:
      action.setCheckable(True)
      if checked:
        action.setChecked(True)
    menu.addAction(action)
    if slot == None:
      action.setDisabled(True)
    else:
      action.triggered.connect(slot)
    if shortcut != None: action.setShortcut(shortcut)
    return action

  ### GUI SLOTS

  def preferences(self):
    dialog = PreferencesDialog(self)
    dialog.exec_()

  def clone_footprint(self):    
    if self.executed_footprint == []:
      s = "Can't clone if footprint doesn't compile."
      QtGui.QMessageBox.warning(self, "warning", s)
      self.status(s) 
      return
    old_code = self.te1.toPlainText()
    old_meta = pycoffee.eval_coffee_meta(old_code)
    dialog = CloneFootprintDialog(self, old_meta, old_code)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = pycoffee.clone_coffee_meta(old_code, old_meta, new_id, new_name)
    lib_dir = QtCore.QDir(self.lib_dir[new_lib])
    new_file_name = lib_dir.filePath("%s.coffee" % (new_id))
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    s = "%s/%s cloned to %s/%s." % (self.active_library, old_meta['name'], new_lib, new_name)
    self.te1.setPlainText(new_code)
    self.rescan_library(new_lib, new_id)
    self.active_footprint_id = new_id
    self.active_library = new_lib
    self.show_footprint_tab()
    self.status(s)

  def reload_footprint(self):
    with open(self.active_footprint_file(), 'r') as f:
      self.te1.setPlainText(f.read())
    self.status("%s reloaded." % (self.active_footprint_file()))

  def new_footprint(self):
    dialog = NewFootprintDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = pycoffee.new_coffee(new_id, new_name)
    lib_dir = QtCore.QDir(self.lib_dir[new_lib])
    new_file_name = lib_dir.filePath("%s.coffee" % (new_id))
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    self.te1.setPlainText(new_code)
    self.rescan_library(new_lib, new_id)
    self.active_footprint_id = new_id
    self.active_library = new_lib
    self.show_footprint_tab()
    self.status("%s/%s created." % (new_lib, new_name))

  def move_footprint(self):
    old_code = self.te1.toPlainText()
    old_meta = pycoffee.eval_coffee_meta(old_code)
    dialog = MoveFootprintDialog(self, old_meta)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_name, new_lib) = dialog.get_data()
    old_name = old_meta['name']
    my_id = self.active_footprint_id
    fn = my_id + '.coffee'
    old_lib = self.active_library
    new_code = old_code.replace("#name %s" % (old_name), "#name %s" % (new_name))
    new_lib_dir = QtCore.QDir(self.lib_dir[new_lib])
    new_file_name = new_lib_dir.filePath(fn)
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    self.te1.setPlainText(new_code)
    self.status("moved %s/%s to %s/%s." % (old_lib, old_name, new_lib, new_name))
    if old_lib == new_lib: 
      self.rescan_library(old_lib, my_id) # just to update the name
    else:
      old_lib_dir = QtCore.QDir(self.lib_dir[old_lib])
      old_lib_dir.remove(fn)
      self.rescan_library(old_lib)
      self.rescan_library(new_lib, my_id)
      self.active_library = new_lib

  def editor_text_changed(self):
    key_idle = self.setting("gui/keyidle")
    if key_idle > 0:
      t = time.time()
      if (t - self.last_time < float(key_idle)/1000.0):
        self.timer.stop()
        self.timer.start(float(key_idle))
        return
      self.last_time = t
      if self.first_keypress:
        self.first_keypress = False
        self.timer.stop()
        self.timer.start(float(key_idle))
        return
    self.first_keypress = True
    self.compile()
    if self.is_fresh_from_file:
      self.is_fresh_from_file = False

  def export_previous(self):
    if self.export_library_filename == "":
      self.export_footprint()
    else:
      self._export_footprint()

  def export_footprint(self):
     dialog = LibrarySelectDialog(self)
     if dialog.exec_() != QtGui.QDialog.Accepted: return
     self.export_library_filename = dialog.filename
     self.export_library_filetype = dialog.filetype
     self._export_footprint()

  def row_changed(self, current, previous):
    x = current.data(QtCore.Qt.UserRole)
    if x == None: return
    (t,x) = x
    if t == 'library':
      self.selected_library = x
      self._tree_library_selected()
      return
    # it is a footprint
    self.selected_library = None
    self._tree_footprint_selected()
    (lib_name, fpid) = x
    directory = self.lib_dir[lib_name]
    fn = fpid + '.coffee'
    ffn = QtCore.QDir(directory).filePath(fn)
    with open(ffn) as f:
      self.te1.setPlainText(f.read())
      self.is_fresh_from_file = True
      self.active_footprint_id = fpid
      self.active_library = lib_name

  def show_footprint_tab(self):
    self.left_qtab.setCurrentIndex(1)

  def close(self):
    QtGui.qApp.quit()

  def zoom(self):
    self.glw.zoomfactor = int(self.zoom_selector.text())
    self.glw.zoom_changed = True
    self.glw.auto_zoom = self.auto_zoom.isChecked()
    #if self.glw.auto_zoom:
    #  self.glw.update_zoomfactor()
    self.glw.updateGL()

  def auto_zoom_changed(self):
    self.settings.setValue('gl/autozoom', str(self.auto_zoom.isChecked()))

  def remove_footprint(self):
    directory = self.lib_dir[self.active_library]
    fn = self.active_footprint_id + '.coffee'
    QtCore.QDir(directory).remove(fn)
    # fall back to first_foot in library, if any
    library = self.rescan_library(self.active_library)
    if library.first_foot != None:
      library.first_foot.select(self.tree_selection_model)
      self.active_footprint_id = library.first_foot.id
      self.active_library = library.first_foot.lib_name
    # else fall back to any first foot...
    else:
      root = self.model.invisibleRootItem()
      for row_index in range(0, root.rowCount()):
        library = root.child(row_index)
        if library.first_foot != None:
          library.first_foot.select(self.tree_selection_model)
          self.active_footprint_id = library.first_foot.id
          self.active_library = library.first_foot.lib_name
    directory = self.lib_dir[self.active_library]
    fn = self.active_footprint_id + '.coffee'
    ffn = QtCore.QDir(directory).filePath(fn)
    with open(ffn) as f:
       self.te1.setPlainText(f.read())
    # else... ?
    # TODO we don't support being completely footless now

  def add_library(self):
    dialog = AddLibraryDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (name, directory) = dialog.get_data()
    self.lib_dir[name] = directory
    self.lib_exist[name] = True
    self.save_libraries()
    root = self.model.invisibleRootItem()
    lib = gui.library.Library(name, directory)
    root.appendRow(lib)
    self.tree.expandAll()

  def reload_library(self):
    if self.selected_library != None:
      lib = self.selected_library
    else:
      lib = self.active_library
    self.rescan_library(lib)
    self.status("%s reloaded." % (lib))

  def disconnect_library(self):
    dialog = DisconnectLibraryDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    lib_name = dialog.get_data()
    del self.lib_dir[lib_name]
    del self.lib_exist[lib_name]
    self.save_libraries()
    root = self.model.invisibleRootItem()
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.name == lib_name: break
    root.removeRow(row_index)
    if lib_name != self.active_library: return
    # select first foot of the first library which contains foots
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.first_foot != None:
        library.first_foot.select(self.tree_selection_model)
        self.active_footprint_id = library.first_foot.id
        self.active_library = library.first_foot.lib_name
        directory = self.lib_dir[self.active_library]
        fn = self.active_footprint_id + '.coffee'
        ffn = QtCore.QDir(directory).filePath(fn)
        with open(ffn) as f:
          self.te1.setPlainText(f.read())
    # TODO we don't support being completely footless now

  def import_footprints(self):
    dialog = ImportFootprintsDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (footprint_names, importer, selected_library) = dialog.get_data()
    lib_dir = QtCore.QDir(self.lib_dir[selected_library])
    l = []
    for footprint_name in footprint_names:
      interim = importer.import_footprint(footprint_name) 
      interim = inter.sort_by_type(interim)
      interim = inter.find_pad_patterns(interim)
      l.append((footprint_name, interim))
    cl = []
    for (footprint_name, interim) in l:
      try:
       coffee = generatesimple.generate_coffee(interim)
       cl.append((footprint_name, coffee))
      except Exception as ex:
        tb = traceback.format_exc()
        s = "warning: skipping footprint %s\nerror: %s" % (footprint_name, str(ex) + '\n' + tb)
        QtGui.QMessageBox.warning(self, "warning", s)
    for (footprint_name, coffee) in cl:
      meta = pycoffee.eval_coffee_meta(coffee)
      new_file_name = lib_dir.filePath("%s.coffee" % (meta['id']))
      with open(new_file_name, 'w+') as f:
        f.write(coffee)
    self.rescan_library(selected_library)
    self.status('Importing done.')

  def docu_changed(self):
    self.display_docu = self.docu_action.isChecked()
    self.settings.setValue('gui/displaydocu', str(self.display_docu))
    self.compile()

  def restrict_changed(self):
    self.display_restrict = self.restrict_action.isChecked()
    self.settings.setValue('gui/displayrestrict', str(self.display_restrict))
    self.compile()

  def stop_changed(self):
    self.display_stop = self.stop_action.isChecked()
    self.settings.setValue('gui/displaystop', str(self.display_stop))
    self.compile()

  ### OTHER METHODS

  def setting(self, key):
    return self.settings.value(key, default_settings[key])

  def library_by_directory(self, directory):
    for x in self.lib_dir.keys():
      if self.lib_dir[x] == directory:
        return x
    return None

  def status(self, s):
    self.statusBar().showMessage(s)

  def update_zoom(self, dx, dy, x1, y1, x2, y2):
    # TODO: keep x1, y1, x2, y2 in account
    w = self.glw.width()
    h = self.glw.height()
    if dx == self.gl_dx and dy == self.gl_dy and w == self.gl_w and h == self.gl_h:
      return
    self.gl_dx = dx
    self.gl_dy = dy
    self.gl_w = w
    self.gl_h = h
    zoomx = float(w) / dx
    zoomy = float(h) / dy
    zoom = int(min(zoomx, zoomy))
    self.zoom_selector.setText(str(zoom))
    self.glw.zoomfactor = zoom
    self.glw.zoom_changed = True

  def compile(self):
    code = self.te1.toPlainText()
    compilation_failed_last_time = self.executed_footprint == []
    self.executed_footprint = []
    try:
      interim = pycoffee.eval_coffee_footprint(code)
      if interim != None:
        interim = inter.cleanup_js(interim)
        interim = inter.add_names(interim)
      self.executed_footprint = interim
      self.te2.setPlainText(str(interim))
      if self.auto_zoom.isChecked():
        (dx, dy, x1, y1, x2, y2) = inter.size(interim)
        self.update_zoom(dx, dy, x1, y1, x2, y2)
      filter_out = []
      if not self.display_docu: filter_out.append('docu')
      if not self.display_restrict: filter_out.append('restrict')
      self.glw.set_shapes(inter.prepare_for_display(interim, filter_out))
      if not self.is_fresh_from_file:
        with open(self.active_footprint_file(), "w+") as f:
          f.write(code)
      if compilation_failed_last_time:
        self.status("Compilation successful.")
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2, 0])
    # TODO: get rid of exception handling code duplication
    except pycoffee.JSError as ex:
      self.executed_footprint = []
      s = str(ex)
      s = s.replace('JSError: Error: ', '')
      self.te2.setPlainText('coffee error:\n' + s)
      self.status(s)
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2-150, 150])
    except (ReferenceError, IndexError, AttributeError, SyntaxError, TypeError, NotImplementedError) as ex:
      self.executed_footprint = []
      self.te2.setPlainText('coffee error:\n' + str(ex))
      print traceback.format_exc()
      self.status(str(ex))
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2-150, 150])
    except RuntimeError as ex:
      if str(ex) == 'maximum recursion depth exceeded while calling a Python object':
        msg = 'Error: please make sure your coffeescript does not contain self-referencing recursive elements because those can\'t be compiled into a result at the moment'
      else:
        tb = traceback.format_exc()
        msg = str(ex) + "\n"+tb
      self.executed_footprint = []
      self.te2.setPlainText(msg)
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2-150, 150])
    except Exception as ex:
      self.executed_footprint = []
      tb = traceback.format_exc()
      self.te2.setPlainText('other error:\n' + str(ex) + "\n"+tb)
      self.status(str(ex))
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2-150, 150])
  
  def _export_footprint(self):
    if self.export_library_filename == "": return
    if self.executed_footprint == []:
      s = "Can't export if footprint doesn't compile."
      QtGui.QMessageBox.warning(self, "warning", s)
      self.status(s) 
      return
    if self.export_library_filetype != 'eagle':
      s = "Only eagle CAD export is currently supported"
      QtGui.QMessageBox.critical(self, "error", s)
      self.status(s)
      return
    try:
      exporter = export.eagle.Export(self.export_library_filename)
      exporter.export_footprint(self.executed_footprint)
      exporter.save()
      self.status("Exported to "+self.export_library_filename+".")
    except Exception as ex:
      self.status(str(ex))
      raise

  def rescan_library(self, name, select_id = None):
    root = self.model.invisibleRootItem()
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.name == name:
        library.scan(select_id)
        if library.selected_foot != None:
          library.selected_foot.select(self.tree_selection_model)
        self.tree.expandAll()
        return library

  def active_footprint_file(self):
   dir = QtCore.QDir(self.lib_dir[self.active_library])
   return dir.filePath(self.active_footprint_id + '.coffee')

  def save_libraries(self):
    l = self.lib_dir.items()
    self.settings.beginWriteArray('library')
    for i in range(len(l)):
      self.settings.setArrayIndex(i)
      self.settings.setValue('name', l[i][0])
      self.settings.setValue('file', l[i][1])
    self.settings.endArray()

  def load_libraries(self):
    size = self.settings.beginReadArray('library')
    for i in range(size):
      self.settings.setArrayIndex(i)
      name = self.settings.value('name')
      filen = self.settings.value('file')
      exists = QtCore.QDir(filen).exists()
      self.lib_dir[name] = filen
      self.lib_exist[name] = exists
    self.settings.endArray()
      
if __name__ == '__main__':
    QtCore.QCoreApplication.setOrganizationName("madparts")
    QtCore.QCoreApplication.setOrganizationDomain("madparts.org")
    QtCore.QCoreApplication.setApplicationName("madparts")
    app = QtGui.QApplication(["madparts"])
    widget = MainWin()
    widget.show()
    app.exec_()
    # on windows we can't delete the file; TODO investigate how to work around that
    if sys.platform != 'win32':
      os.unlink(widget.glw.font_file)
