# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path, re, string, traceback
import pkg_resources
import coffeescript, grind
from inter import inter

import PyV8
import _PyV8
from PyV8 import JSError

supported_formats = ['1.0', '1.1']

# taken from PyV8, but simplified to avoid self-referencing structures
# in a rather primitive way (limiting nesting depth to 5)
# to avoid the out-of-memory error in the python interpreter they introduce
def pyv8_convert(obj, nest=0):
    if nest == 5:
      raise ReferenceError("structure nesting deeper then 5 not allowed")
    nest = nest + 1
    if type(obj) == _PyV8.JSArray:
        return [pyv8_convert(v, nest) for v in obj]

    if type(obj) == _PyV8.JSObject:
        return dict([[str(k), pyv8_convert(obj.__getattr__(str(k)), nest)] for k in obj.__members__])

    return obj

class Global(PyV8.JSClass):

    def require(self, arg):
      file_content = pkg_resources.resource_string(coffeescript.__name__, "%s.js" % (arg))
      return PyV8.JSContext.current.eval(file_content)

js_make_js_from_coffee = None
js_make_js_ctx = None
js_ctx_cleanup_count = 0

def prepare_coffee_compiler():
  global js_make_js_from_coffee
  global js_make_js_ctx
  if js_make_js_from_coffee == None:
      js_make_js_ctx = PyV8.JSContext(Global())
      js_make_js_ctx.enter()
      try:
        js_make_js_from_coffee = js_make_js_ctx.eval("""
(function (coffee_code) {
  CoffeeScript = require('coffee-script');
  js_code = CoffeeScript.compile(coffee_code, {bare:true});
  return js_code;
})
""")
      finally:
        js_make_js_ctx.leave()

# there is probably plenty of room for speeding up things here by
# re-using the generated js from ground and such, however for now it is
# still snappy enough; so let's just keep it simple
def eval_coffee_footprint(coffee):
  meta = eval_coffee_meta(coffee)
  if 'format' not in meta:
    raise Exception("Missing mandatory #format meta field")
  else:
    format = meta['format']
  if format not in supported_formats:
     raise Exception("Unsupported file format. Supported formats: %s" % (supported_formats))
  # only compile the compiler once
  global js_make_js_ctx
  global js_make_js_from_coffee
  global js_ctx_cleanup_count
  js_ctx_cleanup_count = js_ctx_cleanup_count + 1
  # HACK: occationally cleanup the context to avoid compiler slowdown
  # will need a better approach in the future
  if js_ctx_cleanup_count == 10:
    js_make_js_ctx = None
    js_make_js_from_coffee = None
    js_ctx_cleanup_count = 0
  if js_make_js_ctx == None:
    prepare_coffee_compiler()
  try:
    js_make_js_ctx.enter()
    ground = pkg_resources.resource_string(grind.__name__, "ground-%s.coffee" % (format))
    ground_js = js_make_js_from_coffee(ground)
    js = js_make_js_from_coffee(coffee + "\nreturn footprint()\n")
    with PyV8.JSContext() as ctxt:
      js_res = ctxt.eval("(function() {\n" + ground_js + js + "\n}).call(this);\n")
      pl = pyv8_convert(js_res)
      pl.append(meta)
      return pl
  finally:
    js_make_js_ctx.leave()

# TODO: the meta stuff doesn't really belong here

def eval_coffee_meta(coffee):
  lines = coffee.replace('\r', '').split('\n')
  meta_lines = [l for l in lines if re.match('^#\w+',l)]
  meta_list = [re.split('\s',l, 1) for l in meta_lines]
  meta_list = [(l[0][1:], l[1]) for l in meta_list]
  def _collect(acc, (k,v)):
    if k in acc:
      acc[k] = acc[k] + "\n" + v
    else:
      acc[k] = v
    return acc
  return reduce(_collect, meta_list, { 'type': 'meta'})

def clone_coffee_meta(coffee, old_meta, new_id, new_name):
  cl = coffee.splitlines()
  def not_meta_except_desc(s):
    return not re.match('^#\w+',l) or re.match('^#desc \w+', l)
  no_meta_l = [l for l in coffee.splitlines() if not_meta_except_desc(l)]
  no_meta_coffee = '\n'.join(no_meta_l)
  new_meta = "#format 1.1\n#name %s\n#id %s\n#parent %s\n" % (new_name, new_id, old_meta['id'])
  return new_meta + no_meta_coffee

def new_coffee(new_id, new_name):
  return """\
#format 1.1
#name %s
#id %s
#desc TODO

footprint = () ->
  []
""" % (new_name, new_id)

def compile_coffee(code):
  try:
    interim = eval_coffee_footprint(code)
    if interim != None:
      interim = inter.cleanup_js(interim)
      interim = inter.add_names(interim)
      return (None, None, interim)
    else:
      return ('internal error', 'internal error', None)
  except JSError as ex:
    s = str(ex)
    s = s.replace('JSError: Error: ', '')
    return ('coffee error:\n' + s, s, None)
  except (ReferenceError, IndexError, AttributeError, SyntaxError, TypeError, NotImplementedError) as ex:
    print traceback.format_exc()
    return ('coffee error:\n' + str(ex), str(ex), None)
  except RuntimeError as ex:
    if str(ex) == 'maximum recursion depth exceeded while calling a Python object':
      msg = 'Error: please make sure your coffeescript does not contain self-referencing recursive elements because those can\'t be compiled into a result at the moment'
    else:
      tb = traceback.format_exc()
      msg = str(ex) + "\n"+tb
    return (msg, "", None)
  except Exception as ex:
    tb = traceback.format_exc()
    return ('other error:\n' + str(ex) + "\n"+tb, str(ex), None)
