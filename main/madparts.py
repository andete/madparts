#!/usr/bin/env python
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
import coffee.library

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
      library = coffee.library.Library('Examples', example_lib)
      self.lib = {'Examples': library}
      self.save_libraries()
    else:
      self.lib = {}
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

    footprintMenu.addSeparator()
    self.add_action(footprintMenu, '&Force Compile', self.compile, 'Ctrl+F')

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
    self.timer.timeout.connect(self.key_idle_timer_timeout)

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
    first_foot_id = None
    first_foot_lib = None
    for coffee_lib in self.lib.values():
      guilib = gui.library.Library(self.tree_selection_model, coffee_lib)
      parentItem.appendRow(guilib)
      if first:
        first_foot_id = guilib.first_foot_id
        first_foot_lib = guilib
        first = first_foot_id is None
    return (first_foot_lib, first_foot_id)

  def _tree(self):
    tree = QtGui.QTreeView()
    self.tree_selection_model = tree.selectionModel
    (first_foot_lib, first_foot_id) = self._make_model()
    tree.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    tree.setModel(self.model)
    self.tree_selection_model().currentRowChanged.connect(self.row_changed)
    tree.setRootIsDecorated(False)
    tree.expandAll()
    tree.setItemsExpandable(False)
    tree.resizeColumnToContents(0)
    tree.doubleClicked.connect(self.show_footprint_tab)
    self.active_footprint_id = None
    self.active_library = None
    if first_foot_lib is not None:
      print "selected", first_foot_lib.name
      if first_foot_lib.select_first_foot():
        print "selected", first_foot_id
        self.active_footprint_id = first_foot_id
        self.active_library = first_foot_lib.name
    self.tree = tree
    self._tree_footprint_selected()
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
    self.auto_zoom.setChecked(self.setting('gl/autozoom') == 'True')
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
    lib_dir = QtCore.QDir(self.lib[new_lib].directory)
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
    lib_dir = QtCore.QDir(self.lib[new_lib].directory)
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
    new_lib_dir = QtCore.QDir(self.lib[new_lib].directory)
    new_file_name = new_lib_dir.filePath(fn)
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    self.te1.setPlainText(new_code)
    self.status("moved %s/%s to %s/%s." % (old_lib, old_name, new_lib, new_name))
    if old_lib == new_lib: 
      self.rescan_library(old_lib, my_id) # just to update the name
    else:
      old_lib_dir = QtCore.QDir(self.lib[old_lib].directory)
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
    if self.setting('gui/autocompile') == 'True':
      self.compile()
    if self.is_fresh_from_file:
      self.is_fresh_from_file = False

  def key_idle_timer_timeout(self): 
    self.editor_text_changed()

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
    directory = self.lib[lib_name].directory
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
    if self.glw.auto_zoom:
      (dx, dy, x1, y1, x2, y2) = inter.size(self.executed_footprint)
      self.update_zoom(dx, dy, x1, y1, x2, y2, True)
    self.glw.updateGL()

  def auto_zoom_changed(self):
    self.settings.setValue('gl/autozoom', str(self.auto_zoom.isChecked()))

  def remove_footprint(self):
    directory = self.lib[self.active_library].directory
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
    directory = self.lib[self.active_library].directory
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
    lib = coffee.library.Library(name, directory)
    self.lib[name] = lib
    self.save_libraries()
    root = self.model.invisibleRootItem()
    guilib = gui.library.Library(self.tree_selection_model, lib)
    root.appendRow(guilib)
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
    del self.lib[lib_name]
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
      if library.select_first_foot():
        self.active_footprint_id = library.first_foot_id
        self.active_library = library.name
        directory = self.lib[self.active_library].directory
        fn = self.active_footprint_id + '.coffee'
        ffn = QtCore.QDir(directory).filePath(fn)
        with open(ffn) as f:
          self.te1.setPlainText(f.read())
    # TODO we don't support being completely footless now

  def import_footprints(self):
    dialog = ImportFootprintsDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (footprint_names, importer, selected_library) = dialog.get_data()
    lib_dir = QtCore.QDir(self.lib[selected_library].directory)
    l = []
    for footprint_name in footprint_names:
      interim = inter.import_footprint(importer, footprint_name) 
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

  def status(self, s):
    self.statusBar().showMessage(s)

  def update_zoom(self, dx, dy, x1, y1, x2, y2, force=False):
    # TODO: keep x1, y1, x2, y2 in account
    w = self.glw.width()
    h = self.glw.height()
    if dx == self.gl_dx and dy == self.gl_dy and w == self.gl_w and h == self.gl_h:
      if not force: return
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
    (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
    if interim != None:
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
    else:
      self.executed_footprint = []
      self.te2.setPlainText(error_txt)
      self.status(status_txt)
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
        library.scan()
        if select_id is not None:
          library.select(select_id)
        self.tree.expandAll()
        return library

  def active_footprint_file(self):
   dir = QtCore.QDir(self.lib[self.active_library].directory)
   return dir.filePath(self.active_footprint_id + '.coffee')

  def save_libraries(self):
    l = self.lib.values()
    self.settings.beginWriteArray('library')
    for i in range(len(l)):
      self.settings.setArrayIndex(i)
      self.settings.setValue('name', l[i].name)
      self.settings.setValue('file', l[i].directory)
    self.settings.endArray()

  def load_libraries(self):
    size = self.settings.beginReadArray('library')
    for i in range(size):
      self.settings.setArrayIndex(i)
      name = self.settings.value('name')
      filen = self.settings.value('file')
      library = coffee.library.Library(name, filen)
      self.lib[name] = library
    self.settings.endArray()

def gui_main():
  QtCore.QCoreApplication.setOrganizationName("madparts")
  QtCore.QCoreApplication.setOrganizationDomain("madparts.org")
  QtCore.QCoreApplication.setApplicationName("madparts")
  app = QtGui.QApplication(["madparts"])
  widget = MainWin()
  widget.show()
  if widget.glw.glversion < 2.1:
    s = """\
OpenGL 2.1 or better is required (%s found)
(or use software openGL like mesa)""" % (widget.glw.glversion)
    QtGui.QMessageBox.critical(widget, "error", s)
    return
  app.exec_()
  # on windows we can't delete the file; TODO investigate how to work around that
  if sys.platform != 'win32':
    os.unlink(widget.glw.font_file)

if __name__ == '__main__':
    if len(sys.argv) == 1:
      gui_main()
    else:
      import cli
      sys.exit(cli.cli_main())
