#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import glob, sys, os

from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

arch = os.uname()[4]

if sys.platform == 'darwin':
   OPTIONS = {
       'argv_emulation': True,
       #'includes': ['sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'simplejson'],
       #'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
       }
  extra_options = dict(
      setup_requires=['py2app'],
      app=['madparts.py'],
      # Cross-platform applications generally expect sys.argv to
      # be used for opening files.
      options=dict(py2app=OPTIONS),
      )
elif sys.platform == 'win32':
  extra_options = dict(
      setup_requires=['py2exe'],
      app=['madparts.py'],
      )
elif sys.platform.starts_with('linux'):
   extra_options = dict(
       # Normally unix-like platforms will use "setup.py install"
       # and install the main script as such
       scripts=['madparts.py'],
       )
   if not arch in ['i686', 'x86_64']:
     raise Exception("unsupported arch %s" % (arch))
   extern_lib_dir = "extern/linux-%s-2.7" % (arch)
else:
  raise Exception("unsupported platform %s" % (sys.platform))

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
    extern_libs,
    ],
  platforms = ["Windows", "Linux", "Mac OS-X"],
  **extra_options
  )
