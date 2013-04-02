#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import argparse, sys

import coffee.pycoffee as pycoffee
from inter import inter
import export.eagle

def export_footprint(remaining):
  parser = argparse.ArgumentParser(prog=sys.argv[0] + ' export')
  parser.add_argument('footprint', help='footprint file')
  parser.add_argument('library', help='library file')
  args = parser.parse_args(remaining)
  with open(args.footprint, 'r') as f:
    code = f.read()
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  if interim == None:
    print >> sys.stderr, error_txt
    return 1
  meta = filter(lambda x: x['type'] == 'meta', interim)[0]
  name = meta['name']
  print name, 'compiled.'
  library_file = args.library
  try:
    version = export.eagle.check_xml_file(library_file)
  except Exception as ex:
    print >> sys.stderr, str(ex)
    return 1
  exporter = export.eagle.Export(library_file)
  exporter.export_footprint(interim)
  exporter.save()
  print "Exported to "+library_file+"."
  return 0

def import_footprint(remaining):
  print >> sys.stderr, 'Not implemented: import footprint'
  return 1

def cli_main():
  parser = argparse.ArgumentParser()
  parser.add_argument('command', help='command to execute', choices=['import','export'])
  (args, remaining) = parser.parse_known_args()
  if args.command == 'import':
    return import_footprint(remaining)
  else:
    return export_footprint(remaining)

if __name__ == '__main__':
  sys.exit(cli_main())
