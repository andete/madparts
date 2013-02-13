# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore

class Library(QtGui.QStandardItem):

  def scan(self):
    self.removeRows(0, self.rowCount())
    d = QtCore.QDir(self.directory)
    for f in filter(lambda f: f != '.' and f != '..', d.entryList()):
      self.appendRow(QtGui.QStandardItem(f))

  def __init__(self, name, directory):
    super(Library, self).__init__(name + " (" + directory + ")")
    self.name = name
    self.directory = directory
    self.setEditable(False)
    self.scan()
