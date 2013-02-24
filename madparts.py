#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import numpy as np
import math, time, traceback, re

from PySide import QtGui, QtCore

import jydcoffee, jydgldraw, jydlibrary
from syntax.jydjssyntax import JSHighlighter
from syntax.jydcoffeesyntax import CoffeeHighlighter
import export.eagle
from jyddefaultsettings import default_settings
from jyddialogs import *

example_library = ('Example Library', 'library')


class MainWin(QtGui.QMainWindow):

  def __init__(self):
    super(MainWin, self).__init__()

    self.libraries = {example_library[0]:example_library[1]}

    self.settings = QtCore.QSettings()

    splitter = QtGui.QSplitter(self, QtCore.Qt.Horizontal)
    splitter.addWidget(self._left_part())
    splitter.addWidget(self._right_part())
    self.setCentralWidget(splitter)

    self.statusBar().showMessage("Ready.")

    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    exitAction = QtGui.QAction('Quit', self)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(self.close)
    fileMenu.addAction(exitAction)

    footprintMenu = menuBar.addMenu('&Footprint')
    cloneAction = QtGui.QAction('&Clone', self)
    footprintMenu.addAction(cloneAction)
    cloneAction.triggered.connect(self.clone_footprint)
    removeAction = QtGui.QAction('&Remove', self)
    removeAction.triggered.connect(self.remove_footprint)
    footprintMenu.addAction(removeAction)
    newAction = QtGui.QAction('&New', self)
    footprintMenu.addAction(newAction)
    newAction.triggered.connect(self.new_footprint)
    exportAction = QtGui.QAction('&Export previous', self)
    exportAction.setShortcut('Ctrl+E')
    exportAction.triggered.connect(self.export_previous)
    footprintMenu.addAction(exportAction)
    exportdAction = QtGui.QAction('E&xport', self)
    exportdAction.setShortcut('Ctrl+X')
    exportdAction.triggered.connect(self.export_footprint)
    footprintMenu.addAction(exportdAction)

    libraryMenu = menuBar.addMenu('&Library')
    addAction = QtGui.QAction('&Add', self)
    addAction.setDisabled(True)
    libraryMenu.addAction(addAction)
    disconnectAction = QtGui.QAction('&Disconnect', self)
    disconnectAction.setDisabled(True)
    libraryMenu.addAction(disconnectAction)

    helpMenu = menuBar.addMenu('&Help')
    aboutAction = QtGui.QAction("&About", self)
    aboutAction.triggered.connect(self.about)
    helpMenu.addAction(aboutAction)

    self.last_time = time.time() - 10.0
    self.first_keypress = False
    self.timer = QtCore.QTimer()
    self.timer.setSingleShot(True)
    self.timer.timeout.connect(self.editor_text_changed)

    self.executed_footprint = []
    self.export_library_filename = ""
    self.export_library_filetype = ""
    self.is_fresh_from_file = True

  ### GUI HELPERS

  def _settings(self):
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    self.settings_gldx = QtGui.QLineEdit(str(self.setting('gl/dx')))
    self.settings_gldx.setValidator(QtGui.QIntValidator(100,1000))
    form_layout.addRow("GL dx", self.settings_gldx) 
    self.settings_gldy = QtGui.QLineEdit(str(self.setting('gl/dy')))
    self.settings_gldy.setValidator(QtGui.QIntValidator(100,1000))
    form_layout.addRow("GL dy", self.settings_gldy) 
    self.settings_glzoomf = QtGui.QLineEdit(str(self.setting('gl/zoomfactor')))
    self.settings_glzoomf.setValidator(QtGui.QIntValidator(1,250))
    form_layout.addRow("zoom factor", self.settings_glzoomf) 
    font_hbox = QtGui.QHBoxLayout()
    self.settings_font_filename = QtGui.QLineEdit(str(self.setting('gl/fontfile')))
    self.settings_font_filename.setReadOnly(True)
    font_button = QtGui.QPushButton("Browse")
    font_button.clicked.connect(self.get_font)
    font_hbox.addWidget(self.settings_font_filename)
    font_hbox.addWidget(font_button)
    font_widget = QtGui.QWidget()
    font_widget.setLayout(font_hbox)
    form_layout.addRow("font", font_widget) 
    self.settings_key_idle = QtGui.QLineEdit(str(self.setting('gui/keyidle')))
    self.settings_key_idle.setValidator(QtGui.QDoubleValidator(0.0,5.0,2))
    form_layout.addRow("key idle", self.settings_key_idle) 
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.RestoreDefaults
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    rest_but = button_box.button(QtGui.QDialogButtonBox.RestoreDefaults)
    rest_but.clicked.connect(self.settings_restore_defaults)
    button_box.accepted.connect(self.settings_accepted)
    vbox.addWidget(button_box)
    settings_widget = QtGui.QWidget()
    settings_widget.setLayout(vbox)
    return settings_widget

  def _make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(3)
    self.model.setHorizontalHeaderLabels(['name','id','desc'])
    parentItem = self.model.invisibleRootItem()
    first = True
    for (name, directory) in self.libraries.items():
      lib = jydlibrary.Library(name, directory)
      parentItem.appendRow(lib)
      if first:
        first = False
        first_foot = lib.first_footprint()
    return first_foot

  def _tree(self):
    first_foot = self._make_model()
    tree = QtGui.QTreeView()
    tree.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    deleteAction = QtGui.QAction("&Remove", tree)
    deleteAction.triggered.connect(self.remove_footprint)
    tree.addAction(deleteAction)
    cloneAction = QtGui.QAction('&Clone', tree)
    cloneAction.triggered.connect(self.clone_footprint)
    tree.addAction(cloneAction)
    exportAction = QtGui.QAction('&Export previous', tree)
    exportAction.triggered.connect(self.export_previous)
    tree.addAction(exportAction)
    exportdAction = QtGui.QAction('E&xport', tree)
    exportdAction.triggered.connect(self.export_footprint)
    tree.addAction(exportdAction)
    tree.setModel(self.model)
    tree.setRootIsDecorated(False)
    tree.expandAll()
    tree.setItemsExpandable(False)
    self.tree_selection_model = tree.selectionModel()
    self.tree_selection_model.currentRowChanged.connect(self.row_changed)
    tree.doubleClicked.connect(self.show_footprint_tab)
    first_foot.select(self.tree_selection_model)
    self.active_footprint_id = first_foot.id
    self.active_library = first_foot.lib_name
    self.tree = tree
    return tree

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
    lqtab.addTab(self._settings(), "settings")
    lqtab.setCurrentIndex(1)
    self.left_qtab = lqtab
    return lqtab

  def _right_part(self):
    rvbox = QtGui.QVBoxLayout()
    rhbox = QtGui.QHBoxLayout()
    self.glw = jydgldraw.JYDGLWidget(self)
    self.zoom_selector = QtGui.QLineEdit(str(self.glw.zoomfactor))
    self.zoom_selector.setValidator(QtGui.QIntValidator(1, 250))
    self.zoom_selector.editingFinished.connect(self.zoom)
    self.zoom_selector.returnPressed.connect(self.zoom)
    rhbox.addWidget(QtGui.QLabel("Zoom: "))
    rhbox.addWidget(self.zoom_selector)
    rvbox.addLayout(rhbox)
    rvbox.addWidget(self.glw)

    right = QtGui.QWidget()
    right.setLayout(rvbox)
    return right

  def about(self):
    a = """
<p align="center"><b>madparts</b><br/>the functional footprint editor</p>
<p align="center">(c) 2013 Joost Yervante Damad &lt;joost@damad.be&gt;</p>
<p align="center"><a href="http://madparts.org">http://madparts.org</a></p>
"""
    QtGui.QMessageBox.about(self, "about madparts", a)

  ### GUI SLOTS

  def settings_restore_defaults(self):
    self.settings_gldx.setText(str(default_settings['gl/dx']))
    self.settings_gldy.setText(str(default_settings['gl/dy']))
    self.settings_glzoomf.setText(str(default_settings['gl/zoomfactor']))
    self.settings_font_filename.setText(str(default_settings['gl/fontfile']))
    self.settings_key_idle.setText(str(default_settings['gui/keyidle']))

  def settings_accepted(self):
    self.settings.setValue('gl/dx', self.settings_gldx.text())
    self.settings.setValue('gl/dy', self.settings_gldy.text())
    self.settings.setValue('gl/zoomfactor', self.settings_glzoomf.text())
    self.settings.setValue('gl/fontfile', self.settings_font_filename.text())
    self.settings.setValue('gui/keyidle', self.settings_key_idle.text())
    self.status("Settings updated.")

  def get_font(self):
    result = QtGui.QFileDialog.getOpenFileName(self,
      "Select Font", filter="Truetype Font (*.ttf)")
    font_filename = result[0]
    if (font_filename == ''): return
    self.settings_font_filename.setText(font_filename)

  def clone_footprint(self):    
    if self.executed_footprint == []:
      s = "Can't clone if footprint doesn't compile."
      QtGui.QMessageBox.warning(self, "warning", s)
      self.status(s) 
      return
    old_code = self.te1.toPlainText()
    old_meta = jydcoffee.eval_coffee_meta(old_code)
    dialog = CloneFootprintDialog(self, old_meta, old_code)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = jydcoffee.clone_coffee_meta(old_code, old_meta, new_id, new_name)
    lib_dir = QtCore.QDir(self.libraries[new_lib])
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

  def new_footprint(self):
    dialog = NewFootprintDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (new_id, new_name, new_lib) = dialog.get_data()
    new_code = jydcoffee.new_coffee_meta(new_id, new_name)
    lib_dir = QtCore.QDir(self.libraries[new_lib])
    new_file_name = lib_dir.filePath("%s.coffee" % (new_id))
    with open(new_file_name, 'w+') as f:
      f.write(new_code)
    self.te1.setPlainText(new_code)
    self.rescan_library(new_lib, new_id)
    self.active_footprint_id = new_id
    self.active_library = new_lib
    self.show_footprint_tab()
    self.status("%s/%s created." % (new_lib, new_name))

  def editor_text_changed(self):
    key_idle = self.setting("gui/keyidle")
    if key_idle > 0:
      t = time.time()
      if (t - self.last_time < float(key_idle)/1000.0):
        self.timer.stop()
        self.timer.start(key_idle)
        return
      self.last_time = t
      if self.first_keypress:
        self.first_keypress = False
        self.timer.stop()
        self.timer.start(key_idle)
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
    (lib_name, fpid) = x
    if fpid != None:
      directory = self.libraries[lib_name]
      fn = fpid + '.coffee'
      ffn = QtCore.QDir(directory).filePath(fn)
      with open(ffn) as f:
        self.te1.setPlainText(f.read())
        self.is_fresh_from_file = True
        self.active_footprint_id = fpid
        self.active_library = lib_name
    else:
      # TODO jump back to previous ?
      pass

  def show_footprint_tab(self):
    self.left_qtab.setCurrentIndex(1)

  def close(self):
    QtGui.qApp.quit()

  def zoom(self):
    self.glw.zoomfactor = int(self.zoom_selector.text())
    self.glw.zoom_changed = True
    self.glw.updateGL()

  def remove_footprint(self):
    directory = self.libraries[self.active_library]
    fn = self.active_footprint_id + '.coffee'
    QtCore.QDir(directory).remove(fn)
    # fall back to first_foot in library, if any
    library = self.rescan_library(self.active_library)
    if library.first_foot != None:
      library.first_foot.select(self.tree_selection_model)
      return
    # else fall back to any first foot...
    root = self.model.invisibleRootItem()
    for row_index in range(0, root.rowCount()):
      library = root.child(row_index)
      if library.first_foot != None:
        library.first_foot.select(self.tree_selection_model)
    # else... ?
    # we don't support being completely footless now

  ### OTHER METHODS

  def setting(self, key):
    return self.settings.value(key, default_settings[key])

  def library_by_directory(self, directory):
    for x in self.libraries.keys():
      if self.libraries[x] == directory:
        return x
    return None

  def status(self, s):
    self.statusBar().showMessage(s)

  def compile(self):
    def _add_names(res):
      if res == None: return None
      def generate_ints():
        for i in xrange(1, 10000):
          yield i
      g = generate_ints()
      def _c(x):
        if 'type' in x:
          if x['type'] in ['smd', 'pad']:
            x['name'] = str(g.next())
        else:
          x['type'] = 'silk' # default type
        return x
      return [_c(x) for x in res]

    code = self.te1.toPlainText()
    self.executed_footprint = []
    try:
      result = jydcoffee.eval_coffee_footprint(code)
      self.executed_footprint = _add_names(result)
      self.te2.setPlainText(str(self.executed_footprint))
      self.glw.set_shapes(self.executed_footprint)
      if not self.is_fresh_from_file:
        with open(self.active_footprint_file(), "w+") as f:
          f.write(code)
      self.status("Compilation successful.")
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2, 0])
    # TODO: get rid of exception handling code duplication
    except jydcoffee.JSError as ex:
      self.executed_footprint = []
      s = str(ex)
      s = s.replace('JSError: Error: ', '')
      self.te2.setPlainText(s)
      self.status(s)
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2-150, 150])
    except (ReferenceError, IndexError, AttributeError, SyntaxError, TypeError, NotImplementedError) as ex:
      self.executed_footprint = []
      self.te2.setPlainText(str(ex))
      self.status(str(ex))
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2-150, 150])
    except Exception as ex:
      self.executed_footprint = []
      tb = traceback.format_exc()
      self.te2.setPlainText(str(ex) + "\n"+tb)
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
      export.eagle.export(self.export_library_filename, self.executed_footprint)
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
        return library

  def active_footprint_file(self):
   print self.active_library, self.active_footprint_id
   dir = QtCore.QDir(self.libraries[self.active_library])
   return dir.filePath(self.active_footprint_id + '.coffee')
        
      
if __name__ == '__main__':
    QtCore.QCoreApplication.setOrganizationName("madparts")
    QtCore.QCoreApplication.setOrganizationDomain("madparts.org")
    QtCore.QCoreApplication.setApplicationName("madparts")
    app = QtGui.QApplication(["madparts"])
    widget = MainWin()
    widget.show()
    app.exec_()
