#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL


import PyV8
import os.path

class Global(PyV8.JSClass):

    def __init__(self):
      self.path = ""

    def require(self, arg):
      content = ""
      with open(self.path+arg+".js") as file:
        file_content = file.read()
      result = None
      try:
        store_path = self.path
        self.path = self.path + os.path.dirname(arg) + "/"
        result = PyV8.JSContext.current.eval(file_content)
      finally:
        self.path = store_path
      return result

def eval_footprint(js):
  with PyV8.JSContext() as ctxt:
      return PyV8.convert(ctxt.eval(js+"; shapes();"))

test_js = """
function footprint() {
  return { 'x': 0, 'y': 0 }
}
"""

if __name__ == '__main__':
    eval_footprint(test_js)

example = """
function shapes() {
  var dxs = [-2, -1, 0, 1, 2];
  var rect1 = { shape: 'rect', x: 0.8, y: 1};
  function xmod(dx) {
    var b = Object();
    b.shape = rect1.shape;
    b.x = rect1.x; 
    b.y = rect1.y;
    b.dx = dx; return b;
  }
  return dxs.map(xmod);
}
"""
