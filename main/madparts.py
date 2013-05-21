#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import numpy as np
import math, time, traceback, re, os, os.path, sys

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

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

    self.explorer = gui.library.Explorer(self)

    self.settings = QtCore.QSettings()

    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    self.add_action(fileMenu, '&Quit', self.close, 'Ctrl+Q')

    editMenu = menuBar.addMenu('&Edit')
    self.add_action(editMenu, '&Preferences', self.preferences)

    footprintMenu = menuBar.addMenu('&Footprint')
    self.add_action(footprintMenu, '&Clone', self.explorer.clone_footprint, 'Ctrl+Alt+C')
    self.add_action(footprintMenu, '&Delete', self.explorer.remove_footprint, 'Ctrl+Alt+D')
    self.ac_new = self.add_action(footprintMenu, '&New', self.explorer.new_footprint, 'Ctrl+Alt+N')
    self.ac_move = self.add_action(footprintMenu, '&Move', self.explorer.move_footprint, 'Ctrl+Alt+M')
    self.add_action(footprintMenu, '&Export previous', self.export_previous, 'Ctrl+E')
    self.add_action(footprintMenu, '&Export', self.export_footprint, 'Ctrl+Alt+X')
    self.add_action(footprintMenu, '&Print', None, 'Ctrl+P')
    self.add_action(footprintMenu, '&Reload', self.reload_footprint, 'Ctrl+R')
    footprintMenu.addSeparator()

    self.display_docu = self.setting('gui/displaydocu') == 'True'
    self.display_restrict = self.setting('gui/displayrestrict') == 'True'
    self.display_stop = self.setting('gui/displaystop') == 'True'
    self.display_keepout = self.setting('gui/displaykeepout') == 'True'
    self.docu_action = self.add_action(footprintMenu, "&Display Docu", self.docu_changed, checkable=True, checked=self.display_docu)
    self.restrict_action = self.add_action(footprintMenu, "&Display Restrict", self.restrict_changed, checkable=True, checked=self.display_restrict)
    self.stop_action = self.add_action(footprintMenu, "&Display Stop", self.stop_changed, checkable=True, checked=self.display_stop)
    self.keepout_action = self.add_action(footprintMenu, "&Display Keepout", self.keepout_changed, checkable=True, checked=self.display_keepout)

    footprintMenu.addSeparator()
    self.add_action(footprintMenu, '&Force Compile', self.compile, 'Ctrl+F')

    libraryMenu = menuBar.addMenu('&Library')
    self.add_action(libraryMenu, '&Add', self.explorer.add_library)
    self.add_action(libraryMenu, '&Disconnect', self.explorer.disconnect_library)
    self.add_action(libraryMenu, '&Import', self.import_footprints, 'Ctrl+Alt+I')
    self.add_action(libraryMenu, '&Reload', self.explorer.reload_library, 'Ctrl+Alt+R')

    helpMenu = menuBar.addMenu('&Help')
    self.add_action(helpMenu, '&About', self.about)

    self.explorer.initialize_libraries(self.settings)

    splitter = QtGui.QSplitter(self, QtCore.Qt.Horizontal)

    splitter.addWidget(self._left_part())
    splitter.addWidget(self._right_part())
    self.setCentralWidget(splitter)

    self.last_time = time.time() - 10.0
    self.first_keypress = False
    self.timer = QtCore.QTimer()
    self.timer.setSingleShot(True)
    self.timer.timeout.connect(self.key_idle_timer_timeout)

    self.executed_footprint = []
    self.export_library_filename = ""
    self.export_library_filetype = ""
    self.gl_dx = 0
    self.gl_dy = 0
    self.gl_w = 0
    self.gl_h = 0

    self.statusBar().showMessage("Ready.")

  ### GUI HELPERS

  def set_code_textedit_readonly(self, readonly):
    self.code_textedit.setReadOnly(readonly)
    pal = self.code_textedit.palette()
    if not self.explorer.has_footprint(): 
      pal.setColor(QtGui.QPalette.Base, Qt.darkGray)
    elif self.explorer.active_footprint.readonly:
      pal.setColor(QtGui.QPalette.Base, Qt.lightGray)
    else:
      pal.setColor(QtGui.QPalette.Base, Qt.white)
    self.code_textedit.setPalette(pal)

  def set_library_readonly(self, readonly):
    self.ac_new.setDisabled(readonly)
    self.ac_move.setDisabled(readonly)

  def _footprint(self):
    lsplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
    self.code_textedit = QtGui.QTextEdit()
    self.code_textedit.setAcceptRichText(False)
    if self.explorer.has_footprint():
      with open(self.explorer.active_footprint_file()) as f:
        self.code_textedit.setPlainText(f.read())
      self.set_code_textedit_readonly(self.explorer.active_footprint.readonly)
    else:
      self.set_code_textedit_readonly(True)
    self.highlighter1 = CoffeeHighlighter(self.code_textedit.document())
    self.code_textedit.textChanged.connect(self.editor_text_changed)
    self.result_textedit = QtGui.QTextEdit()
    self.result_textedit.setReadOnly(True)
    self.highlighter2 = JSHighlighter(self.result_textedit.document())
    lsplitter.addWidget(self.code_textedit)
    lsplitter.addWidget(self.result_textedit)
    self.lsplitter = lsplitter
    [s1, s2] = lsplitter.sizes()
    lsplitter.setSizes([min(s1+s2-150, 150), 150])
    return lsplitter  

  def _left_part(self):
    lqtab = QtGui.QTabWidget()
    self.explorer.populate()
    lqtab.addTab(self.explorer, "library")
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

  def reload_footprint(self):
    with open(self.explorer.active_footprint_file(), 'r') as f:
      self.code_textedit.setPlainText(f.read())
    self.status("%s reloaded." % (self.explorer.active_footprint_file()))

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

  def import_footprints(self):
    dialog = ImportFootprintsDialog(self)
    if dialog.exec_() != QtGui.QDialog.Accepted: return
    (footprint_names, importer, selected_library) = dialog.get_data()
    lib_dir = QtCore.QDir(self.explorer.coffee_lib[selected_library].directory)
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
    self.explorer.rescan_library(selected_library)
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

  def keepout_changed(self):
    self.display_keepout = self.keepout_action.isChecked()
    self.settings.setValue('gui/displaykeepout', str(self.display_keepout))
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
    zoomx = 0.0
    zoomy = 0.0
    if dx > 0.0:
      zoomx = float(w) / dx
    if dy > 0.0:
      zoomy = float(h) / dy
    if zoomx == 0.0 and zoomy == 0.0:
      zoomx = 42 
      zoomy = 42
    zoom = int(min(zoomx, zoomy))
    self.zoom_selector.setText(str(zoom))
    self.glw.zoomfactor = zoom
    self.glw.zoom_changed = True

  def compile(self):
    code = self.code_textedit.toPlainText()
    if code == "": return
    compilation_failed_last_time = self.executed_footprint == []
    self.executed_footprint = []
    (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
    if interim != None:
      self.executed_footprint = interim
      self.result_textedit.setPlainText(str(interim))
      if self.auto_zoom.isChecked():
        (dx, dy, x1, y1, x2, y2) = inter.size(interim)
        self.update_zoom(dx, dy, x1, y1, x2, y2)
      filter_out = []
      if not self.display_docu: filter_out.append('docu')
      if not self.display_restrict: filter_out.append('restrict')
      if not self.display_stop: filter_out.append('stop')
      if not self.display_keepout: filter_out.append('keepout')
      self.glw.set_shapes(inter.prepare_for_display(interim, filter_out))
      if not self.explorer.active_footprint.readonly:
        with open(self.explorer.active_footprint_file(), "w+") as f:
          f.write(code)
      if compilation_failed_last_time:
        self.status("Compilation successful.")
      [s1, s2] = self.lsplitter.sizes()
      self.lsplitter.setSizes([s1+s2, 0])
    else:
      self.executed_footprint = []
      self.result_textedit.setPlainText(error_txt)
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
    return 1
  return app.exec_()
