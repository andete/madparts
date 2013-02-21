# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

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
      t = export.eagle.Export().check(self.filename)
      self.filetype = 'eagle'
      self.lib_type.setText(t)
      self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(False)
      self.button_box.button(QtGui.QDialogButtonBox.Ok).setFocus()
    except Exception as ex:
      QtGui.QMessageBox.critical(self, "error", str(ex))
      
