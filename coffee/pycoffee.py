# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path, re, string

import PyV8

supported_formats = ['1.0']

grind_dir = os.path.abspath(os.path.dirname(__file__)+'/../grind')


from PyV8 import JSError

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

js_make_js_from_coffee = None
js_make_js_ctx = None

def prepare_coffee_compiler():
  global js_make_js_from_coffee
  global js_make_js_ctx
  if js_make_js_from_coffee == None:
      js_make_js_ctx = PyV8.JSContext(Global())
      js_make_js_ctx.enter()
      try:
        js_make_js_from_coffee = js_make_js_ctx.eval("""
(function (coffee_code) {
  CoffeeScript = require('coffee-script/coffee-script');
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
  if js_make_js_ctx == None:
    prepare_coffee_compiler()
  try:
    js_make_js_ctx.enter()
    with open("%s/ground-%s.coffee" % (grind_dir, format)) as f: ground = f.read()
    ground_js = js_make_js_from_coffee(ground)
    js = js_make_js_from_coffee(coffee + "\nreturn footprint()\n")
    with PyV8.JSContext() as ctxt:
      js_res = ctxt.eval("(function() {\n" + ground_js + js + "\n}).call(this);\n")
      pl = PyV8.convert(js_res)
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
  new_meta = "#format 1.0\n#name %s\n#id %s\n#parent %s\n" % (new_name, new_id, old_meta['id'])
  return new_meta + no_meta_coffee

def new_coffee(new_id, new_name):
  return """\
#format 1.0
#name %s
#id %s
#desc TODO

footprint = () ->
  []
""" % (new_name, new_id)
