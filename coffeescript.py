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

def make_js(coffee_script_code):
  with PyV8.JSContext(Global()) as ctxt:
    js_make_js_from_coffee = ctxt.eval("""
(function (coffee_code) {
  CoffeeScript = require('coffee-script/coffee-script');
  js_code = CoffeeScript.compile(coffee_code, null);
  return js_code;
})
""")
    return js_make_js_from_coffee(coffee_script_code)

coffee_script_code = """
yearsOld = max: 10, ida: 9, tim: 11

ages = for child, age of yearsOld
  "#{child} is #{age}"
return ages
"""

js_code = make_js(coffee_script_code)

print js_code

with PyV8.JSContext() as ctxt:
  print PyV8.convert(ctxt.eval(js_code))
