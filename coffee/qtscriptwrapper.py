#!/usr/bin/python2

import os
import os.path
from PySide import QtCore
from PySide.QtCore import QObject
from PySide.QtScript import QScriptEngine
from PySide.QtScript import QScriptValue
from PySide.QtGui import QApplication
from PySide.QtCore import QCoreApplication

# This class is a QObject that gets wrapped as a javascript object, to provide
# the callback for the "require" call. See comments in JsEngine for why this
# isn't just a wrapped function instead of a QObject...
class JsEngineRequireClass(QObject):
  def __init__(self, engine):
    super(JsEngineRequireClass, self).__init__()
    self.engine = engine
  @QtCore.Slot(str, result=QScriptValue)
  def require(self, arg):
    data_dir = os.environ['DATA_DIR']
    filename = os.path.join(data_dir, 'coffeescript', "%s.js" % (arg))
    with open(filename) as f:
      file_content = f.read()
    try:
      ret = self.engine.evaluate(file_content, "%s.js" % (arg))
      return ret
    except JsEngineException as ex:
      raise ex

# Converts javascript objects to python objects. Tries to be a bit fancy and
# wrap functions. Objects that are not basic types or functions are not
# converted.
def scriptValueToPyObject(value):
  if value.isFunction():
    return lambda *x: scriptValueToPyObject(value.call(value.scope(), list(x)))
  if value.isVariant():
    pass
  elif value.isObject():
    return value
  ret = value.toVariant()
  if ("toPyObject" in dir(ret)):
    ret = ret.toPyObject()
  return ret
    
# Function to convert python objects to javascript objects. Tries to be a bit
# fancy and wrap things like functions. Things that are already javascript
# objects are left as-is, of course.
def pyObjectToScriptValue(engine, value):
  if (isinstance(value, QScriptValue)):
    return value
  if (("__call__" in dir(value)) and ("func_name" in dir(value))):
    f = lambda context,engine: pyObjectToScriptValue(engine, func(*_contextToArguments(context)))
    return engine.newFunction(f)
  if (isinstance(value, QObject)):
    return engine.newQObject(value)
  return engine.newVariant(value)

# Converts a javascript context to a list of arguments
def _contextToArguments(context):
  ret = []
  for i in range(context.argumentCount()):
    ret.append(scriptValueToPyObject(context.argument(i)))
  return ret

# Class for representing javascript engine exceptions
class JsEngineException(Exception):
  def __init__(self, result, engine):
    super(JsEngineException, self).__init__()
    self.line = engine.uncaughtExceptionLineNumber()
    self.message = result.toString()
  def __repr__(self):
    return "%s(%d, \"%s\")" % (str(self.__class__), self.line, self.message)
  def __str__(self):
    return "QtScript exception at line %d: %s" % (self.line, self.message)
  def getLine(self):
    return self.line
  def getMessage(self):
    return self.message

# Class to wrap the QScriptEngine
class JsEngine:
  def __init__(self):
    self.app = QApplication.instance()
    if self.app is None:
      self.app = QCoreApplication([])
    self.engine = QScriptEngine()
    self.globalObject = self.engine.globalObject()
    
    # There were some problems evalating javascript inside a function callback. QtSide's bindings for QScriptEngine
    # didn't seem prepared to handle it (it breaks in weird hard-to-debug ways)
    # It is however not a problem if you use a wrapped QObject for the callback instead of using engine.newFunction().
    # The workaround here is to pass a wrapped QObject, and then evaluate javascript to create a function that calls
    # a method of the wrapped QObject.
    # Also note: Wrapped QObjects passed to QtSide are not refcounted in Python! To work around this, a reference to
    #            "RequireObj" is stored in the JSEngine instance
    self.requireObj = JsEngineRequireClass(self.engine)
    self.addObject('RequireObj', self.requireObj)
    self.evaluate("""
function require(arg) {
  return RequireObj.require(arg);
}
    """)
  
  # Sets a variable in the global object
  def addObject(self, name, obj):
    wrappedObject = pyObjectToScriptValue(self.engine, obj)
    self.engine.globalObject().setProperty(name, wrappedObject)
  
  # Adds a python function to the global object, wrapping it
  def addFunction(self, name, func):
    f = lambda context,engine: pyObjectToScriptValue(engine, func(*_contextToArguments(context)))
    wrappedFunction = self.engine.newFunction(f)
    self.engine.globalObject().setProperty(name, wrappedFunction)
    
  # Adds a python function to the global object, not wrapping it (it gets passed raw context and engine arguments)
  def addRawFunction(self, name, func):
    wrappedFunction = self.engine.newFunction(func)
    self.engine.globalObject().setProperty(name, wrappedFunction)

  # Evaluate some javascript code
  def evaluate(self, code):
    result = self.engine.evaluate(code)
    if self.engine.hasUncaughtException():
      raise JsEngineException(result, self.engine)
    return scriptValueToPyObject(result)

if __name__ == '__main__':
  engine = JsEngine()
  engine.evaluate("print('Hello World');")
