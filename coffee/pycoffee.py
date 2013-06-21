# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path, re, string, traceback
from inter import inter

from qtscriptwrapper import JsEngine
from qtscriptwrapper import scriptValueToPyObject
from qtscriptwrapper import JsEngineException

supported_formats = ['1.0', '1.1', '1.2']

js_make_js_from_coffee = None
js_make_js_ctx = None
js_ctx_cleanup_count = 0

def prepare_coffee_compiler():
  global js_make_js_from_coffee
  global js_make_js_ctx
  if js_make_js_from_coffee == None:
      js_make_js_ctx = JsEngine()
      try:
        js_make_js_from_coffee = js_make_js_ctx.evaluate("""
CoffeeScript = require('coffee-script');
(function (coffee_code) {
  js_code = CoffeeScript.compile(coffee_code, {bare:true});
  return js_code;
})
""")
      except JsEngineException as ex:
        raise ex
      finally:
        pass

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
    data_dir = os.environ['DATA_DIR']
    filename = os.path.join(data_dir, 'grind', "ground-%s.coffee" % (format))
    with open(filename) as f:
      ground = f.read()
    
    ground_js = js_make_js_from_coffee(ground)
    js = js_make_js_from_coffee(coffee + "\nreturn footprint()\n")
    
    # If the code returned is an error, raise an exception
    if ("isError" in dir(js) and js.isError()):
      raise Exception(js.toString())
    
    js_res = js_make_js_ctx.evaluate("(function() {\n" + ground_js + js + "\n}).call(this);\n")
    pl = js_res.toVariant()
    pl.append(meta)
    return pl
  finally:
    pass

# TODO: the meta stuff doesn't really belong here

def eval_coffee_meta(coffee):
  coffee = str(coffee)
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
  new_meta = "#format 1.2\n#name %s\n#id %s\n#parent %s\n" % (new_name, new_id, old_meta['id'])
  return new_meta + no_meta_coffee

def new_coffee(new_id, new_name):
  return """\
#format 1.2
#name %s
#id %s
#desc TODO

footprint = () ->
  []
""" % (new_name, new_id)

def preprocess_coffee(code):
  def repl(m):
    t = m.group(2)
    i = float(m.group(1))
    if t == 'mi' or t == 'mil':
      return str(i*0.0254)
    elif t == 'in':
      return str(i*25.4)
    else:
      return m.group(0)
  return re.sub('([-+]?[0-9]*\.?[0-9]+)([im][ni]l?)', repl, code)

def compile_coffee(code):
  try:
    preprocessed = preprocess_coffee(code)
    interim = eval_coffee_footprint(preprocessed)
    if interim != None:
      interim = inter.cleanup_js(interim)
      interim = inter.add_names(interim)
      return (None, None, interim)
    else:
      return ('internal error', 'internal error', None)
  except JsEngineException as ex:
    s = ex.getMessage()
    return ('coffee error:\n' + s, s, None)
  except Exception as ex:
    tb = traceback.format_exc()
    return ('other error:\n' + str(ex) + "\n"+tb, str(ex), None)
