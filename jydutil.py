# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

def oget(m, k, d):
  if k in m: return m[k]
  return d

def fget(m, k, d = 0.0):
  return float(oget(m, k, d))

def iget(m, k, d = 0.0):
  return int(oget(m, k, d))

def eget(m, k, e):
  if k in m: return m[k]
  raise Exception(e)

def type_to_layer(shape):
  t = shape['type']
  if t == 'label':
    value = shape['value']
    if value == 'NAME':
      t = 'name'
    elif value == 'VALUE':
      t = 'value'
  type_to_layer_dict = {
    'smd': 'top',
    'label': 'silk',
     'name': 'name',
     'value': 'value',
     'silk': 'silk',
    }
  return type_to_layer_dict[t]
