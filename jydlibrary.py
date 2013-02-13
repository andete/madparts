# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui

class Library(QtGui.QStandardItem):

  def __init__(self, name, directory):
    super(Library, self).__init__(name + " (" + directory + ")")
    self.directory = directory
