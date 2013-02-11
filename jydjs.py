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

def make_js_from_coffee(coffee_script_code):
  with PyV8.JSContext(Global()) as ctxt:
    js_make_js_from_coffee = ctxt.eval("""
(function (coffee_code) {
  CoffeeScript = require('coffee-script/coffee-script');
  js_code = CoffeeScript.compile(coffee_code, {bare:true});
  return js_code;
})
""")
    return js_make_js_from_coffee(coffee_script_code)

def eval_coffee_footprint(coffee):
  with open("ground.coffee") as f: ground = f.read()
  ground_js = make_js_from_coffee(ground)
  js = make_js_from_coffee(coffee + "\nreturn footprint()\n")
  with PyV8.JSContext() as ctxt:
      return PyV8.convert(ctxt.eval("(function() {\n" + ground_js + js + "\n}).call(this);\n"))
