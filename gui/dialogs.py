# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import uuid
import os.path

from PySide import QtGui, QtCore

from defaultsettings import default_settings, color_schemes

import export.detect as detect

def color_scheme_combo(parent, current):
  l_combo = QtGui.QComboBox()
  for k in color_schemes.keys():
    l_combo.addItem(k, k)
    if k == current:
      l_combo.setCurrentIndex(l_combo.count()-1)
  return l_combo

def library_combo(explorer, allow_non_existing=False, allow_readonly=False):
  l_combo = QtGui.QComboBox()
  selected = explorer.selected_library
  if selected == None:
    selected = explorer.active_library.name
  for lib in explorer.coffee_lib.values():
    l_combo.addItem(lib.name, lib.directory)
    if (not lib.exists and not allow_non_existing) or (lib.readonly and not allow_readonly):
      i = l_combo.model().index(l_combo.count()-1, 0) 
      # trick to make disabled
      l_combo.model().setData(i, 0, QtCore.Qt.UserRole-1)
      # if the prefered selected is our disabled one, don't use it
      if selected == lib.name: selected = None
    elif selected == None:
      selected = lib.name
    if lib.name == selected:
      l_combo.setCurrentIndex(l_combo.count()-1)
  return l_combo

class FDFileDialog(QtGui.QFileDialog):
  def __init__(self, parent, txt):
    super(FDFileDialog, self).__init__(parent, txt)
    self.currentChanged.connect(self.current_changed)

  def current_changed(self, path):
    if os.path.isdir(path) and ".pretty" in path:
      self.setFileMode(QtGui.QFileDialog.Directory)
    else:
      self.setFileMode(QtGui.QFileDialog.ExistingFile)

def select_library(obj):
  qf = FDFileDialog(obj, 'Select Library')
  qf.setFilter("CAD Library (*.lbr *.xml *.pretty *.mod *.kicad_mod)")
  if qf.exec_() == 0: return None
  result = qf.selectedFiles()
  filename = result[0]
  if (filename == ''): return
  #try:
  (t, version) = detect.detect(filename)
  return (t, version, filename)
  #except Exception as ex:
  #  QtGui.QMessageBox.critical(obj, "error", str(ex))
  #  return None

# Used in Export Footprint from the menu
class LibrarySelectDialog(QtGui.QDialog):

  def __init__(self, parent=None):
    super(LibrarySelectDialog, self).__init__(parent)
    self.setWindowTitle('Select Library')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
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
    self.lib_type = QtGui.QLineEdit()
    self.lib_type.setReadOnly(True)
    form_layout.addRow("type", self.lib_type) 
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_file(self):
    result = select_library(self)
    if result == None: return
    (self.filetype, self.version, self.filename) = result
    self.lib_filename.setText(self.filename)
    self.lib_type.setText(self.filetype + " " + self.version)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(False)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setFocus()

class ImportFootprintsDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(ImportFootprintsDialog, self).__init__(parent)
    self.setWindowTitle('Import Footprints')
    self.resize(640,640) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
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
    form_layout.addRow("import from:", lib_widget) 
    self.lib_type = QtGui.QLineEdit()
    self.lib_type.setReadOnly(True)
    form_layout.addRow("type", self.lib_type) 
    vbox.addLayout(form_layout)
    vbox.addWidget(QtGui.QLabel("select footprint(s):"))
    tree = QtGui.QTreeView()
    tree.setModel(self.make_model())
    tree.setRootIsDecorated(False)
    tree.resizeColumnToContents(0)
    tree.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
    self.tree_selection_model = tree.selectionModel()
    self.tree_selection_model.selectionChanged.connect(self.selection_changed)
    vbox.addWidget(tree)
    form_layout2 = QtGui.QFormLayout()
    self.l_combo = library_combo(parent.explorer)
    form_layout2.addRow("import to:", self.l_combo)
    vbox.addLayout(form_layout2)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)
 
  def get_file(self):
    result = select_library(self)
    if result == None: return
    (self.filetype, version, self.filename) = result
    self.lib_filename.setText(self.filename)
    self.lib_type.setText(version)
    self.populate_model()

  def make_model(self):
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(1)
    self.model.setHorizontalHeaderLabels(['name'])
    self.root = self.model.invisibleRootItem()
    return self.model

  def populate_model(self):
    self.root.removeRows(0, self.root.rowCount())
    self.importer = detect.make_importer(self.filename)
    name_desc_list = self.importer.list_names()
    name_desc_list = sorted(name_desc_list, lambda (n1,d1),(n2,d2): cmp(n1,n2))
    for (name, desc) in name_desc_list:
      name_item = QtGui.QStandardItem(name)
      name_item.setToolTip(desc)
      name_item.setEditable(False)
      self.root.appendRow([name_item])

  def selection_changed(self, selected, deselected):
    has = self.tree_selection_model.hasSelection()
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(not has)

  def get_data(self):
    indices = self.tree_selection_model.selectedIndexes()
    return ([self.model.data(i) for i in indices], self.importer, self.l_combo.currentText())

class PreferencesDialog(QtGui.QDialog):

  def __init__(self, parent):
    super(PreferencesDialog, self).__init__(parent)
    self.parent = parent
    vbox = QtGui.QVBoxLayout()
    form_layout = QtGui.QFormLayout()
    self.gldx = QtGui.QLineEdit(str(parent.setting('gl/dx')))
    self.gldx.setValidator(QtGui.QIntValidator(100,1000))
    form_layout.addRow("GL dx", self.gldx) 
    self.gldy = QtGui.QLineEdit(str(parent.setting('gl/dy')))
    self.gldy.setValidator(QtGui.QIntValidator(100,1000))
    form_layout.addRow("GL dy", self.gldy) 
    self.glzoomf = QtGui.QLineEdit(str(parent.setting('gl/zoomfactor')))
    self.glzoomf.setValidator(QtGui.QIntValidator(1,250))
    form_layout.addRow("zoom factor", self.glzoomf) 
    self.auto_compile = QtGui.QCheckBox("Auto Compile")
    self.auto_compile.setChecked(parent.setting('gui/autocompile')=='True')
    form_layout.addRow("auto compile", self.auto_compile) 
    self.key_idle = QtGui.QLineEdit(str(parent.setting('gui/keyidle')))
    self.key_idle.setValidator(QtGui.QDoubleValidator(0.0,5.0,2))
    form_layout.addRow("key idle", self.key_idle) 
    self.color_scheme = color_scheme_combo(self, str(parent.setting('gl/colorscheme')))
    form_layout.addRow("color scheme", self.color_scheme) 
    vbox.addLayout(form_layout)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.RestoreDefaults | QtGui.QDialogButtonBox.Cancel
    button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    rest_but = button_box.button(QtGui.QDialogButtonBox.RestoreDefaults)
    rest_but.clicked.connect(self.settings_restore_defaults)
    button_box.accepted.connect(self.settings_accepted)
    button_box.rejected.connect(self.reject)
    vbox.addWidget(button_box)
    self.setLayout(vbox)

  def settings_restore_defaults(self):
    self.gldx.setText(str(default_settings['gl/dx']))
    self.gldy.setText(str(default_settings['gl/dy']))
    self.glzoomf.setText(str(default_settings['gl/zoomfactor']))
    self.auto_compile.setChecked(default_settings['gui/autocompile'])
    self.key_idle.setText(str(default_settings['gui/keyidle']))
    default_color_scheme = str(default_settings['gui/colorscheme'])
    for i in range(0, self.color_scheme.count()):
      if self.color_scheme.itemText(i) == default_color_scheme:
        self.color_scheme.setCurrentIndex(i)
        break

  def settings_accepted(self):
    settings = self.parent.settings
    settings.setValue('gl/dx', self.gldx.text())
    settings.setValue('gl/dy', self.gldy.text())
    settings.setValue('gl/zoomfactor', self.glzoomf.text())
    settings.setValue('gui/autocompile', str(self.auto_compile.isChecked()))
    settings.setValue('gui/keyidle', self.key_idle.text())
    settings.setValue('gl/colorscheme', self.color_scheme.currentText())
    self.parent.status("Settings updated.")
    self.accept()
