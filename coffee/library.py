# (c) 2013-2015 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, glob

import coffee.pycoffee as pycoffee

class Meta:

  def __init__(self, meta):
    if not 'desc' in meta:
      meta['desc'] = ''
    if not 'parent' in meta:
      meta['parent'] = None
    self.meta = meta
    for k in meta:
      self.__dict__[k] = meta[k]
    self.child_ids = []

class Library:

  def __init__(self, name, directory):
    self.name = name
    self.directory = directory
    self.exists = os.path.exists(self.directory)
    self.is_dir = True
    self.readonly = False
    if self.exists:
      self.is_dir = os.path.isdir(self.directory)
      self.readonly = not os.access(self.directory, os.W_OK)
    self.meta_list = []
    self.fail_list = []
    self.meta_by_id = {}
    self.scan()

  def scan(self, select_id = None):
    self.meta_list = []
    self.fail_list = []
    if not self.exists: return
    for path in glob.glob(self.directory + '/*.coffee'):
      with open(path) as f:
        code = f.read()
      meta = pycoffee.eval_coffee_meta(code)
      if not 'name' in meta or not 'id' in meta: 
        self.fail_list.append(meta)
        continue
      meta['readonly'] = not os.access(path, os.W_OK)
      meta['filename'] = path
      self.meta_list.append(meta)
    self.meta_list = [Meta(meta) for meta in self.meta_list]
    self.meta_list.sort(key=lambda x: x.name)
    self.meta_by_id = {}
    for meta in self.meta_list:
      self.meta_by_id[meta.id] = meta
    self.meta_by_name = {}
    for meta in self.meta_list:
      self.meta_by_name[meta.name] = meta
    # scan child relationships
    found_as_child = []
    for meta in self.meta_list:
      if meta.parent != None and meta.parent in self.meta_by_id:
        self.meta_by_id[meta.parent].child_ids.append(meta.id)
        found_as_child.append(meta.id)
    self.root_meta_list = filter(lambda meta: meta.id not in found_as_child, self.meta_list)
