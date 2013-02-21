#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import numpy as np
import math
import time
import traceback
import re

from PySide import QtGui, QtCore

import jydcoffee
from syntax.jydjssyntax import JSHighlighter
from syntax.jydcoffeesyntax import CoffeeHighlighter
import jydgldraw
import jydlibrary
import export.eagle
import jyddefaultsettings as default

libraries = [('Example Library', 'library')]

class ExportDialog(QtGui.QDialog):

  def accept(self):
    print "accepted"
    QtGui.QDialog.accept(self)

  def reject(self):
    print "rejected"
    QtGui.QDialog.reject(self)

  def get_file(self):
    result = QtGui.QFileDialog.getOpenFileName(self,
      "Select Library", filter="Eagle CAD Library (*.lbr);;XML file (*.xml)")
    self.filename = result[0]
    self.lib_filename.setText(self.filename)
    if (self.filename == ''): return

  def __init__(self, parent=None):
    super(ExportDialog, self).__init__(parent)
    self.setWindowTitle('Export Dialog')
    self.resize(640,240) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)
    button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
    form_layout = QtGui.QFormLayout()
    lib_widget = QtGui.QWidget()
    lib_hbox = QtGui.QHBoxLayout()
    self.lib_filename = QtGui.QLineEdit()
    self.lib_filename.setReadOnly(True)
    self.lib_filename.setPlaceholderText("press Browse")
    lib_button = QtGui.QPushButton("Browse")
    self.filename = None
    lib_button.clicked.connect(self.get_file)

    lib_hbox.addWidget(self.lib_filename)
    lib_hbox.addWidget(lib_button)
    lib_widget.setLayout(lib_hbox)
    form_layout.addRow("library", lib_widget) 
    form_layout.addRow("type", QtGui.QLabel("TODO")) 
    vbox.addLayout(form_layout)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

class MainWin(QtGui.QMainWindow):

  def zoom(self):
      self.glw.zoomfactor = int(self.zoom_selector.text())
      self.glw.zoom_changed = True
      self.glw.updateGL()

  def compile(self):
    def _add_names(res):
      if res == None: return None
      def generate_ints():
        for i in range(1, 10000):
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
    try:
      result = jydcoffee.eval_coffee_footprint(code)
      self.result = _add_names(result)
      self.te2.setPlainText(str(result))
      self.glw.set_shapes(result)
      if not self.is_fresh_from_file:
        with open(self.active_file_name, "w+") as f:
          f.write(code)
    except Exception as ex:
      self.te2.setPlainText(str(ex))
      traceback.print_exc()
      
  
  def text_changed(self):
    if self.key_idle > 0:
      t = time.time()
      if (t - self.last_time < float(self.key_idle)/1000.0):
        self.timer.stop()
        self.timer.start(self.key_idle)
        return
      self.last_time = t
      if self.first_keypress:
        self.first_keypress = False
        self.timer.stop()
        self.timer.start(self.key_idle)
        return
    self.first_keypress = True
    self.compile()
    if self.is_fresh_from_file:
      self.is_fresh_from_file = False

  def generate(self):
     export.eagle.Generate()(self.result)

  def export_footprint(self):
     self.export_dialog = ExportDialog(self)
     self.export_dialog.exec_()

  def _footprint(self):
    lsplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
    self.te1 = QtGui.QTextEdit()
    self.te1.setAcceptRichText(False)
    with open(self.active_file_name) as f:
        self.te1.setPlainText(f.read())
    self.highlighter1 = CoffeeHighlighter(self.te1.document())
    self.te1.textChanged.connect(self.text_changed)
    self.te2 = QtGui.QTextEdit()
    self.te2.setReadOnly(True)
    self.highlighter2 = JSHighlighter(self.te2.document())
    lsplitter.addWidget(self.te1)
    lsplitter.addWidget(self.te2)
    return lsplitter

  def _settings(self):
    return QtGui.QLabel("TODO")

  def _make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(3)
    self.model.setHorizontalHeaderLabels(['name','id','desc'])
    parentItem = self.model.invisibleRootItem()
    first = True
    for (name, directory) in libraries:
      lib = jydlibrary.Library(name, directory)
      parentItem.appendRow(lib)
      if first:
        first = False
        first_foot = lib.first_footprint()
    return first_foot

  def row_changed(self, current, previous):
    fn = current.data(jydlibrary.Path_Role)
    if fn != None and re.match('^.+\.coffee$', fn) != None:
      with open(fn) as f:
        self.te1.setPlainText(f.read())
        self.is_fresh_from_file = True
        self.active_file_name = fn
    else:
      # TODO jump back to previous ?
      pass

  def row_double_clicked(self):
    self.left_qtab.setCurrentIndex(1)

  def _tree(self):
    first_foot = self._make_model()
    tree = QtGui.QTreeView()
    tree.setModel(self.model)
    selection_model = tree.selectionModel()
    selection_model.currentRowChanged.connect(self.row_changed)
    tree.doubleClicked.connect(self.row_double_clicked)
    first_foot.select(selection_model)
    self.active_file_name = first_foot.path
    self.tree = tree
    self.is_fresh_from_file = True
    return tree

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
    gldx = self.settings.value("gl/gldx", default.gldx)
    gldy = self.settings.value("gl/gldy", default.gldy)
    font_file = self.settings.value("gl/fontfile", default.font_file)
    start_zoomfactor = self.settings.value("gl/zoomfactor", default.zoomfactor)
    self.glw = jydgldraw.JYDGLWidget(gldx, gldy, str(font_file), start_zoomfactor)
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
<p align="center"><a href="http://madparts.org">madparts.org</a></p>
"""
    QtGui.QMessageBox.about(self, "about madparts", a)
  
  def __init__(self):
    super(MainWin, self).__init__()

    self.settings = QtCore.QSettings()

    self.key_idle = self.settings.value("gui/keyidle", default.key_idle)

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
    cloneAction.setDisabled(True)
    footprintMenu.addAction(cloneAction)
    removeAction = QtGui.QAction('&Remove', self)
    removeAction.setDisabled(True)
    footprintMenu.addAction(removeAction)
    exportAction = QtGui.QAction('&Export', self)
    exportAction.setShortcut('Ctrl+E')
    exportAction.triggered.connect(self.export_footprint)
    footprintMenu.addAction(exportAction)
    exportdAction = QtGui.QAction('E&xport fresh', self)
    exportdAction.setShortcut('Ctrl+X')
    exportdAction.triggered.connect(self.export_footprint)
    footprintMenu.addAction(exportdAction)


    libraryMenu = menuBar.addMenu('&Library')
    createAction = QtGui.QAction('&Create', self)
    createAction.setDisabled(True)
    disconnectAction = QtGui.QAction('&Disconnect', self)
    disconnectAction.setDisabled(True)
    libraryMenu.addAction(createAction)
    libraryMenu.addAction(disconnectAction)

    helpMenu = menuBar.addMenu('&Help')
    aboutAction = QtGui.QAction("&About", self)
    aboutAction.triggered.connect(self.about)
    helpMenu.addAction(aboutAction)

    self.last_time = time.time() - 10.0
    self.first_keypress = False
    self.timer = QtCore.QTimer()
    self.timer.setSingleShot(True)
    self.timer.timeout.connect(self.text_changed)
    self.result = ""

    def close(self):
        QtGui.qApp.quit()
    
if __name__ == '__main__':
    QtCore.QCoreApplication.setOrganizationName("teluna")
    QtCore.QCoreApplication.setOrganizationDomain("madparts.org")
    QtCore.QCoreApplication.setApplicationName("madparts")
    app = QtGui.QApplication(["madparts"])
    widget = MainWin()
    widget.show()
    app.exec_()
