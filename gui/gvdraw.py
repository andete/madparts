# (c) 2014 Joost Yervante Damad <joost@damad.be>
# License: GPL

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class JYDGVWidget(QtGui.QGraphicsView):

  def __init__(self, parent):
    self.scene = QtGui.QGraphicsScene()
    super(JYDGVWidget, self).__init__(self.scene, parent)
    self.scene.addText('Hello, world')
    self.zoomfactor = 42
    self.is_gl = False
