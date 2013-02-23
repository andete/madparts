# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import uuid

from PySide import QtGui, QtCore

import export.eagle

class LibrarySelectDialog(QtGui.QDialog):

  def __init__(self, parent=None):
    super(LibrarySelectDialog, self).__init__(parent)
    self.setWindowTitle('Select Library')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
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
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_file(self):
    result = QtGui.QFileDialog.getOpenFileName(self,
      "Select Library", filter="Eagle CAD Library (*.lbr);;XML file (*.xml)")
    self.filename = result[0]
    self.lib_filename.setText(self.filename)
    if (self.filename == ''): return
    try:
      t = export.eagle.check(self.filename)
      self.filetype = 'eagle'
      self.lib_type.setText(t)
      self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(False)
      self.button_box.button(QtGui.QDialogButtonBox.Ok).setFocus()
    except Exception as ex:
      QtGui.QMessageBox.critical(self, "error", str(ex))
      

class CloneFootprintDialog(QtGui.QDialog):

  def __init__(self, parent, old_meta, old_code):
    super(CloneFootprintDialog, self).__init__(parent)
    libraries = parent.libraries
    self.library = parent.library_by_directory(parent.active_library)
    self.new_id = uuid.uuid4().hex
    self.setWindowTitle('Clone Footprint')
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    gbox_existing = QtGui.QGroupBox("existing")
    gbox_new = QtGui.QGroupBox("new")
    existing_fl = QtGui.QFormLayout()
    existing_fl.addRow("name:", QtGui.QLabel(old_meta['name']))
    existing_fl.addRow("id:", QtGui.QLabel(old_meta['id']))
    existing_fl.addRow("library:", QtGui.QLabel(self.library))
    gbox_existing.setLayout(existing_fl)
    vbox.addWidget(gbox_existing) 
    self.nameLineEdit = QtGui.QLineEdit()
    self.nameLineEdit.setText(old_meta['name']+"_"+self.new_id)
    new_fl = QtGui.QFormLayout()
    new_fl.addRow("name:", self.nameLineEdit)
    new_fl.addRow("id:", QtGui.QLabel(self.new_id))
    self.l_combo = QtGui.QComboBox()
    for x in libraries.items():
      self.l_combo.addItem(x[0], x)
      if x == self.library:
        self.l_combo.setCurrentIndex(self.l_combo.count()-1)
    new_fl.addRow("library:", self.l_combo)
    gbox_new.setLayout(new_fl)
    vbox.addWidget(gbox_new) 
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_data(self):
    return (self.new_id, self.nameLineEdit.text(), self.l_combo.currentText())
