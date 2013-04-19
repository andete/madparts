#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import argparse, sys, traceback, os.path, glob

import coffee.pycoffee as pycoffee
import coffee.generatesimple as generatesimple
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
  try:
    version = export.eagle.check_xml_file(args.library)
  except Exception as ex:
    print >> sys.stderr, str(ex)
    return 1
  exporter = export.eagle.Export(args.library)
  exporter.export_footprint(interim)
  exporter.save()
  print "Exported to "+args.library+"."
  return 0

def import_footprint(remaining):
  parser = argparse.ArgumentParser(prog=sys.argv[0] + ' import')
  parser.add_argument('library', help='library file')
  parser.add_argument('footprint', help='footprint name')
  args = parser.parse_args(remaining)
  try:
    version = export.eagle.check_xml_file(args.library)
  except Exception as ex:
    print >> sys.stderr, str(ex)
    return 1
  importer = export.eagle.Import(args.library)
  names = map(lambda (a,_): a, importer.list_names())
  if not args.footprint in names:
    print >> sys.stderr, "Footprint %s not found in %s." % (args.footprint, args.library)
    return 1
  interim = inter.import_footprint(importer, args.footprint) 
  try:
    coffee = generatesimple.generate_coffee(interim)
  except Exception as ex:
    tb = traceback.format_exc()
    print >> sys.stderr, "Footprint %s\nerror: %s" % (args.footprint, str(ex) + '\n' + tb)
    return 1
  meta = pycoffee.eval_coffee_meta(coffee)
  new_file_name = "%s.coffee" % (meta['id'])
  with open(new_file_name, 'w+') as f:
    f.write(coffee)
  print "%s/%s written to %s." % (args.library, args.footprint, new_file_name)
  return 0

def _list_directory(dirname):
  for path in glob.glob(dirname + '/*.coffee'):
    with open(path) as f:
      code = f.read()
    meta = pycoffee.eval_coffee_meta(code)
    if not 'name' in meta:
      raise Exception('Error loading footprint from %s' % (path))
    print meta['id'], meta['name']
  return 0

def list_library(remaining):
  parser = argparse.ArgumentParser(prog=sys.argv[0] + ' list')
  parser.add_argument('library', help='library file')
  args = parser.parse_args(remaining)
  if os.path.isdir(args.library):
    return _list_directory(args.library)
  try:
    version = export.eagle.check_xml_file(args.library)
  except Exception as ex:
    print >> sys.stderr, str(ex)
    return 1
  importer = export.eagle.Import(args.library)
  names = map(lambda (a,_): a, importer.list_names())
  for name in names: print name
  return 0

def cli_main():
  parser = argparse.ArgumentParser()
  parser.add_argument('command', help='command to execute', 
    choices=['import','export', 'list'])
  (args, remaining) = parser.parse_known_args()
  if args.command == 'import':
    return import_footprint(remaining)
  elif args.command == 'export':
    return export_footprint(remaining)
  else:
    return list_library(remaining)

if __name__ == '__main__':
  sys.exit(cli_main())
