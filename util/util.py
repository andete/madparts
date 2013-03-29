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

def generate_ints():
  for i in xrange(1, 10000):
    yield i

def f_eq(a, b):
  return abs(a-b) < 1E-8

def f_neq(a, b):
  return not f_eq(a, b)

def list_combine(l):
  l2 = []
  for x in l: l2 = l2 + x
  return l2
