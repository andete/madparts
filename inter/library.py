# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os, os.path, glob
import coffee.pycoffee as pycoffee

class Library:

  def __init__(self, name, directory):
    self.name = name
    self.directory = directory
    self.readonly = not os.access(self.directory, os.W_OK)
    self.meta_list = []
    self.fail_list = []
    self._scan()

  def _scan(self, select_id = None):
    self.meta_list = []
    self.fail_list = []
    for path in glob.glob(self.directory + '/*.coffee'):
      with open(path) as f:
        code = f.read()
      meta = pycoffee.eval_coffee_meta(code)
      if not 'name' in meta or not 'id' in meta: 
        self.fail_list.append(meta)
        continue
      meta['readonly'] = not os.access(self.directory, os.W_OK)
      self.meta_list.append(meta)
    self.meta_list.sort(cmp=lambda x,y: cmp(x['name'], y['name']))
    self.meta_by_id = {}
    for meta in self.meta_list:
      self.meta_by_id[meta['id']] = meta
    self.meta_by_name = {}
    for meta in self.meta_list:
      self.meta_by_name[meta['name']] = meta
