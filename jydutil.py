# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

def oget(m, k, d):
  if k in m: return m[k]
  return d

def fget(m, k, d = 0.0):
  return float(oget(m, k, d))

def eget(m, k, e):
  if k in m: return m[k]
  raise Exception(e)
