#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import glob, sys

from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

if sys.platform == 'darwin':
  extra_options = dict(
      setup_requires=['py2app'],
      app=['madparts'],
      # Cross-platform applications generally expect sys.argv to
      # be used for opening files.
      options=dict(py2app=dict(argv_emulation=True)),
      )
elif sys.platform == 'win32':
  extra_options = dict(
      setup_requires=['py2exe'],
      app=['madparts'],
      )
else:
   extra_options = dict(
       # Normally unix-like platforms will use "setup.py install"
       # and install the main script as such
       scripts=['madparts'],
       )

setup(
  name = 'madparts',
  description = 'a functional footprint editor',
  long_description = long_description,
  author = 'Joost Yervante Damad',
  author_email = 'joost@damad.be',
  version = '1.0',
  url = 'http://madparts.org/',
  packages = [
        'coffee', 
        'coffee-script', 
        'export', 
        'grind',
        'gui',
        'inter', 
        'shaders', 
        'syntax', 
        'util',
        ],
  package_data= { 
        'coffee-script': ['*.js', 'LICENSE', 'README'],
        'grind': ['*.coffee'],
        'shaders': ['*.vert', '*.frag'],
        'gui': ['../GPL', '../README.md'], # dirty trick ;)
        },
  data_files = [
    ('share/madparts/contrib/freefont', glob.glob('contrib/freefont/*')),
    ('share/madparts/examples', glob.glob('examples/*.coffee')),
    ],
  platforms = ["Windows", "Linux", "Mac OS-X"],
  **extra_options
  )
