# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from nose.tools import *
from functools import partial
import copy, shutil, os

from bs4 import BeautifulSoup

import coffee.pycoffee as pycoffee
import coffee.generatesimple as generatesimple
from inter import inter
import export.eagle
import export.kicad

assert_multi_line_equal.im_class.maxDiff = None

def _export_eagle(code, expected):
  eagle_lib = 'test/eagle_empty.lbr'
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  assert interim != None
  version = export.eagle.check_xml_file(eagle_lib)
  assert version == 'Eagle CAD 6.4 library'
  exporter = export.eagle.Export(eagle_lib)
  exporter.export_footprint(interim)
  data = exporter.get_pretty_data()
  assert_multi_line_equal(expected, data)

def _export_eagle_package(code, expected_name, expected):
  eagle_lib = 'test/eagle_empty.lbr'
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  assert interim != None
  version = export.eagle.check_xml_file(eagle_lib)
  assert version == 'Eagle CAD 6.4 library'
  exporter = export.eagle.Export(eagle_lib)
  eagle_name = exporter.export_footprint(interim)
  assert eagle_name == expected_name
  data = exporter.get_pretty_footprint(eagle_name)
  # print data
  assert_multi_line_equal(expected, data)
  # print code, expected
  return data

def _assert_equal_no_meta(expected, actual):
  a2 = '\n'.join(filter(lambda l: len(l) > 0 and l[0] != '#', actual.splitlines()))
  e2 = '\n'.join(filter(lambda l: len(l) > 0 and l[0] != '#', expected.splitlines()))
  assert_multi_line_equal(e2, a2)

def _import_eagle_package(eagle_package_xml, import_name, expected):
  eagle_lib = 'test/foo.lbr'
  shutil.copyfile('test/eagle_empty.lbr', eagle_lib)
  try:
    importer = export.eagle.Import(eagle_lib)
    # trick to get our package xml into the empty eagle library
    package_soup = BeautifulSoup(eagle_package_xml, 'xml')
    package_soup.is_xml = False
    importer.soup.drawing.packages.append(package_soup)
    with open(eagle_lib, 'w+') as f:
      f.write(str(importer.soup))
    importer = export.eagle.Import(eagle_lib)
    interim = inter.import_footprint(importer, import_name) 
    assert interim != None
    coffee = generatesimple.generate_coffee(interim)
    # print coffee
    _assert_equal_no_meta(expected, coffee)
  finally:
    os.unlink(eagle_lib)

def _export_kicad_package(code, expected_name, expected):
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  assert interim != None
  exporter = export.kicad.Export("dummy.kicad_mod")
  kicad_name = exporter.export_footprint(interim)
  assert kicad_name == expected_name
  assert_multi_line_equal(expected, exporter.get_string())

def _import_kicad_package(kicad_s, import_name, expected_coffee):
  try:
    kicad_lib = 'test/foo.kicad_mod'
    with open(kicad_lib, "w+") as f:
      f.write(kicad_s)
    importer = export.kicad.Import(kicad_lib)
    interim = inter.import_footprint(importer, import_name) 
    coffee = generatesimple.generate_coffee(interim)
    _assert_equal_no_meta(expected_coffee, coffee)
  finally:
    os.unlink(kicad_lib)

def test_export_eagle_full_lib():
   code = """\
#format 1.1
#name DIL16
#id 2ba395a2e67a49bd9defdf961b264e9f
#parent 5162a77450f545079d5716a7c67b2b42
footprint = () ->
 
  n = 16
  e = 2.54
  between = 7.62
  diameter = 1.2
  drill = 0.8
  line_width = 0.3
  outer_y = n*e/4
  half = between/2

  name = new Name outer_y+e/3
  value = new Value -outer_y-e/3

  pad = new LongPad diameter, drill
  l = dual [pad], n, e, between

  # make first pad round
  l[1-1].shape = 'disc'
  l[1-1].r = diameter*3/4

  silk1 = new Line line_width
  silk1.x1 = half-diameter-0.5
  silk1.y1 = outer_y
  silk1.x2 = half-diameter-0.5
  silk1.y2 = -outer_y

  silk2 = rotate180 clone silk1

  silk3 = new Line line_width
  silk3.y1 = outer_y
  silk3.x1 = half-diameter-0.5
  silk3.y2 = outer_y
  silk3.x2 = -half+diameter+0.5

  silk4 = rotate180 clone silk3

  silks = [silk1, silk2, silk3, silk4]

  combine [l,name,silks,value]
"""

   expected = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="6.4">
 <drawing>
  <settings>
   <setting alwaysvectorfont="no"/>
   <setting verticaltext="up"/>
  </settings>
  <grid altdistance="0.01" altunit="inch" altunitdist="inch" display="no" distance="0.1" multiple="1" style="lines" unit="inch" unitdist="inch"/>
  <layers>
   <layer active="yes" color="4" fill="1" name="Top" number="1" visible="yes"/>
   <layer active="yes" color="1" fill="3" name="Route2" number="2" visible="no"/>
   <layer active="yes" color="4" fill="3" name="Route3" number="3" visible="no"/>
   <layer active="yes" color="1" fill="4" name="Route4" number="4" visible="no"/>
   <layer active="yes" color="4" fill="4" name="Route5" number="5" visible="no"/>
   <layer active="yes" color="1" fill="8" name="Route6" number="6" visible="no"/>
   <layer active="yes" color="4" fill="8" name="Route7" number="7" visible="no"/>
   <layer active="yes" color="1" fill="2" name="Route8" number="8" visible="no"/>
   <layer active="yes" color="4" fill="2" name="Route9" number="9" visible="no"/>
   <layer active="yes" color="1" fill="7" name="Route10" number="10" visible="no"/>
   <layer active="yes" color="4" fill="7" name="Route11" number="11" visible="no"/>
   <layer active="yes" color="1" fill="5" name="Route12" number="12" visible="no"/>
   <layer active="yes" color="4" fill="5" name="Route13" number="13" visible="no"/>
   <layer active="yes" color="1" fill="6" name="Route14" number="14" visible="no"/>
   <layer active="yes" color="4" fill="6" name="Route15" number="15" visible="no"/>
   <layer active="yes" color="1" fill="1" name="Bottom" number="16" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Pads" number="17" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Vias" number="18" visible="yes"/>
   <layer active="yes" color="6" fill="1" name="Unrouted" number="19" visible="yes"/>
   <layer active="yes" color="15" fill="1" name="Dimension" number="20" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tPlace" number="21" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bPlace" number="22" visible="yes"/>
   <layer active="yes" color="15" fill="1" name="tOrigins" number="23" visible="yes"/>
   <layer active="yes" color="15" fill="1" name="bOrigins" number="24" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tNames" number="25" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bNames" number="26" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tValues" number="27" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bValues" number="28" visible="yes"/>
   <layer active="yes" color="7" fill="3" name="tStop" number="29" visible="no"/>
   <layer active="yes" color="7" fill="6" name="bStop" number="30" visible="no"/>
   <layer active="yes" color="7" fill="4" name="tCream" number="31" visible="no"/>
   <layer active="yes" color="7" fill="5" name="bCream" number="32" visible="no"/>
   <layer active="yes" color="6" fill="3" name="tFinish" number="33" visible="no"/>
   <layer active="yes" color="6" fill="6" name="bFinish" number="34" visible="no"/>
   <layer active="yes" color="7" fill="4" name="tGlue" number="35" visible="no"/>
   <layer active="yes" color="7" fill="5" name="bGlue" number="36" visible="no"/>
   <layer active="yes" color="7" fill="1" name="tTest" number="37" visible="no"/>
   <layer active="yes" color="7" fill="1" name="bTest" number="38" visible="no"/>
   <layer active="yes" color="4" fill="11" name="tKeepout" number="39" visible="yes"/>
   <layer active="yes" color="1" fill="11" name="bKeepout" number="40" visible="yes"/>
   <layer active="yes" color="4" fill="10" name="tRestrict" number="41" visible="yes"/>
   <layer active="yes" color="1" fill="10" name="bRestrict" number="42" visible="yes"/>
   <layer active="yes" color="2" fill="10" name="vRestrict" number="43" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Drills" number="44" visible="no"/>
   <layer active="yes" color="7" fill="1" name="Holes" number="45" visible="no"/>
   <layer active="yes" color="3" fill="1" name="Milling" number="46" visible="no"/>
   <layer active="yes" color="7" fill="1" name="Measures" number="47" visible="no"/>
   <layer active="yes" color="7" fill="1" name="Document" number="48" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Reference" number="49" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tDocu" number="51" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bDocu" number="52" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Nets" number="91" visible="yes"/>
   <layer active="yes" color="1" fill="1" name="Busses" number="92" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Pins" number="93" visible="no"/>
   <layer active="yes" color="4" fill="1" name="Symbols" number="94" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Names" number="95" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Values" number="96" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Info" number="97" visible="yes"/>
   <layer active="yes" color="6" fill="1" name="Guide" number="98" visible="yes"/>
  </layers>
  <library>
   <packages>
    <package name="DIL16">
     <description>
      &lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 2ba395a2e67a49bd9defdf961b264e9f
 parent: 5162a77450f545079d5716a7c67b2b42
     </description>
     <pad diameter="1.8" drill="0.8" name="1" rot="R180" shape="round" x="-3.81" y="8.89"/>
     <pad drill="0.8" name="2" rot="R180" shape="long" x="-3.81" y="6.35"/>
     <pad drill="0.8" name="3" rot="R180" shape="long" x="-3.81" y="3.81"/>
     <pad drill="0.8" name="4" rot="R180" shape="long" x="-3.81" y="1.27"/>
     <pad drill="0.8" name="5" rot="R180" shape="long" x="-3.81" y="-1.27"/>
     <pad drill="0.8" name="6" rot="R180" shape="long" x="-3.81" y="-3.81"/>
     <pad drill="0.8" name="7" rot="R180" shape="long" x="-3.81" y="-6.35"/>
     <pad drill="0.8" name="8" rot="R180" shape="long" x="-3.81" y="-8.89"/>
     <pad drill="0.8" name="9" rot="R0" shape="long" x="3.81" y="-8.89"/>
     <pad drill="0.8" name="10" rot="R0" shape="long" x="3.81" y="-6.35"/>
     <pad drill="0.8" name="11" rot="R0" shape="long" x="3.81" y="-3.81"/>
     <pad drill="0.8" name="12" rot="R0" shape="long" x="3.81" y="-1.27"/>
     <pad drill="0.8" name="13" rot="R0" shape="long" x="3.81" y="1.27"/>
     <pad drill="0.8" name="14" rot="R0" shape="long" x="3.81" y="3.81"/>
     <pad drill="0.8" name="15" rot="R0" shape="long" x="3.81" y="6.35"/>
     <pad drill="0.8" name="16" rot="R0" shape="long" x="3.81" y="8.89"/>
     <text align="center" layer="25" size="1.0" x="0.0" y="11.0066666667">
      &gt;NAME
     </text>
     <wire layer="21" width="0.3" x1="2.11" x2="2.11" y1="10.16" y2="-10.16"/>
     <wire layer="21" width="0.3" x1="-2.11" x2="-2.11" y1="-10.16" y2="10.16"/>
     <wire layer="21" width="0.3" x1="2.11" x2="-2.11" y1="10.16" y2="10.16"/>
     <wire layer="21" width="0.3" x1="-2.11" x2="2.11" y1="-10.16" y2="-10.16"/>
     <text align="center" layer="27" size="1.0" x="0.0" y="-11.0066666667">
      &gt;VALUE
     </text>
    </package>
   </packages>
   <symbols>
   </symbols>
   <devicesets>
   </devicesets>
  </library>
 </drawing>
</eagle>"""

   _export_eagle(code, expected)

def test_eagle_footprint1():
  code = """\
#format 1.1
#name PIN 1X2
#id 708e13cc5f4e43f7833af53070ba5078
#desc 2 pin pinheader
footprint = () ->

  d = 2.54
  drill = 1
  w = 0.15
  pad_r = (d-0.34)/2
  n = 2

  name = new Name (n*d/2+1)
  value = new Value (-n*d/2-1)
  
  pad = new RoundPad pad_r, drill

  silk1 = new Line w
  silk1.x1 = d/2
  silk1.y1 = -d/4
  silk1.x2 = d/2
  silk1.y2 = d/4
  silk2 = rotate90 clone silk1
  silk3 = rotate90 clone silk2
  silk4 = rotate90 clone silk3

  silk5 = new Line w
  silk5.y1 = d/4
  silk5.x1 = d/2
  silk5.y2 = d/2
  silk5.x2 = d/4
  silk6 = rotate90 clone silk5
  silk7 = rotate90 clone silk6
  silk8 = rotate90 clone silk7

  unit = [pad, silk1, silk2, silk3, silk4, silk5, silk6, silk7, silk8]

  units = single unit, n, d

  combine [name,value, units]
"""
  expected = """\
<package name="PIN_1X2">
 <description>
  2 pin pinheader
&lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 708e13cc5f4e43f7833af53070ba5078
 </description>
 <text align="center" layer="25" size="1.0" x="0.0" y="3.54">
  &gt;NAME
 </text>
 <text align="center" layer="27" size="1.0" x="0.0" y="-3.54">
  &gt;VALUE
 </text>
 <pad diameter="2.2" drill="1.0" name="1" rot="R0" shape="round" x="0.0" y="1.27"/>
 <wire layer="21" width="0.15" x1="1.27" x2="1.27" y1="0.635" y2="1.905"/>
 <wire layer="21" width="0.15" x1="0.635" x2="-0.635" y1="2.54" y2="2.54"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-1.27" y1="1.905" y2="0.635"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="0.635" y1="0.0" y2="0.0"/>
 <wire layer="21" width="0.15" x1="1.27" x2="0.635" y1="1.905" y2="2.54"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="-1.27" y1="2.54" y2="1.905"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-0.635" y1="0.635" y2="0.0"/>
 <wire layer="21" width="0.15" x1="0.635" x2="1.27" y1="0.0" y2="0.635"/>
 <pad diameter="2.2" drill="1.0" name="2" rot="R0" shape="round" x="0.0" y="-1.27"/>
 <wire layer="21" width="0.15" x1="1.27" x2="1.27" y1="-1.905" y2="-0.635"/>
 <wire layer="21" width="0.15" x1="0.635" x2="-0.635" y1="0.0" y2="0.0"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-1.27" y1="-0.635" y2="-1.905"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="0.635" y1="-2.54" y2="-2.54"/>
 <wire layer="21" width="0.15" x1="1.27" x2="0.635" y1="-0.635" y2="0.0"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="-1.27" y1="0.0" y2="-0.635"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-0.635" y1="-1.905" y2="-2.54"/>
 <wire layer="21" width="0.15" x1="0.635" x2="1.27" y1="-2.54" y2="-1.905"/>
</package>"""
  _export_eagle_package(code, 'PIN_1X2', expected)

_one_coffee = """\
#format 1.1
#name TEST_EAGLE
#id 708e13cc5f4e43f7833af53070ba5078
#desc eagle test
footprint = () ->
  %s = new %s
  combine [%s]
"""

_one_coffee_eagle = """\
<package name="TEST_EAGLE">
 <description>
  eagle test
&lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 708e13cc5f4e43f7833af53070ba5078
 </description>
 %s
</package>"""

def _eagle_pad(diameter, drill, rot, shape, x, y):
  return """<pad diameter="%s" drill="%s" name="1" rot="R%s" shape="%s" x="%s" y="%s"/>""" % (diameter, drill, rot, shape, x, y)

def _eagle_smd(dx, dy, rot, roundness, x, y):
  return """<smd dx="%s" dy="%s" layer="1" name="1" rot="R%s" roundness="%s" x="%s" y="%s"/>""" % (dx, dy, rot, roundness, x, y)

def _code_pad(t, args, mods):
  if t == 'Smd':
    varname = 'smd1'
  else:
    varname = 'pad1'
  sargs = map(lambda a: str(a), args)
  if len(sargs) == 0:
    v = t
  else:
    v = "%s %s" % (t, ', '.join(sargs)) 
  smods = sorted(mods, cmp=lambda (a,b),(c,d): cmp(a,c))
  for mod in smods:
    v = v + ("\n  %s" % (varname)) + (".%s = %s" % mod)
  return v

_one_coffee_tests = [
 ([_code_pad, 'RoundPad', [0.5, 0.5], []], 
  [_eagle_pad, 1.0, 0.5, 0, 'round', 0.0, 0.0]),

 ([_code_pad, 'SquarePad', [1.0, 0.5], []], 
  [_eagle_pad, 1.0, 0.5, 0, 'square', 0.0, 0.0]), 

 ([_code_pad, 'LongPad', [1.0, 0.5], []],  
  [_eagle_pad, 1.0, 0.5, 0, 'long', 0.0, 0.0]),

 ([_code_pad, 'OctagonPad', [0.5, 0.5], []],  
  [_eagle_pad, 1.0, 0.5, 0, 'octagon', 0.0, 0.0]),

 ([_code_pad, 'LongPad', [1.0, 0.5], []],  
  [_eagle_pad, 1.0, 0.5, 0, 'long', 0.0, 0.0]),

 ([_code_pad, 'OffsetPad', [1.0, 0.5], []],  
  [_eagle_pad, 1.0, 0.5, 0, 'offset', 0.0, 0.0]),

 ([_code_pad, 'Smd', [], [('dx',1.0),('dy', 0.3)]], 
  [_eagle_smd, 1.0, 0.3, 0, 0, 0.0, 0.0]),
]

def _no_mod(a,b):
  return (a,b)

def _mod_x(code, eagle):
  code[3].append(('x', 7.3))
  eagle[5] = 7.3
  return (code, eagle)

def _mod_y(code, eagle):
  code[3].append(('y', -4.2))
  eagle[6] = -4.2
  return (code, eagle) 

def _mod_rotate(rot, code, eagle):
  code[3].append(('rot', rot))
  eagle[3] = rot
  return (code, eagle)

def test_eagle_export_one():
  def _eagle_do(d, mod):
    (code_list, item_list) = mod(*d)
    code_func = code_list[0]
    code_args = code_list[1:]
    code_text = code_func(*code_args)
    if code_args[0] == 'Smd':
      varname = 'smd1'
    else:
      varname = 'pad1'
    code = _one_coffee % (varname, code_text, varname)
    item_func = item_list[0]
    item_args = item_list[1:]
    item_text = item_func(*item_args)
    expected = _one_coffee_eagle % (item_text)
    data = _export_eagle_package(code, 'TEST_EAGLE', expected)
  mods = [
    _no_mod, _mod_x, _mod_y, 
    partial(_mod_rotate, 90), partial(_mod_rotate, 180),
    partial(_mod_rotate, 270)
    ]
  for mod in mods:
    for d in _one_coffee_tests:
      d2 = copy.deepcopy(d)
      yield _eagle_do, d2, mod

reimported_coffee_polygon = """\
footprint = () ->
  silk1 = new Line 0.2
  silk1.x1 = 1.41421356237
  silk1.y1 = 1.41421356237
  silk1.x2 = -1.41421356237
  silk1.y2 = -1.41421356237
  silk1.curve = 180.0
  silk2 = new Polygon 0.1
  silk2.start 1.0, -4.0
  silk2.add -1.0, -4.0
  silk2.add -1.0, -3.0
  silk2.add -0.0, -2.0, -90.0
  silk2.end -70.0
  silk3 = new Polygon 0.05
  silk3.start 1.1, 1.2
  silk3.add 1.1, 0.2
  silk3.add 0.1, 1.2
  silk3.end 0.0
  silk4 = new Line 0.075
  silk4.x1 = 2.0
  silk4.y1 = -1.0
  silk4.x2 = 1.0
  silk4.y2 = -0.5
  silk4.curve = 30.0
  docu1 = new Polygon 0.1
  docu1.start 0.0, 1.0
  docu1.add -1.0, 0.0, 180.0
  docu1.add 0.0, -1.0, 180.0
  docu1.add 1.0, 0.0, -10.0
  docu1.end -10.0
  docu1.type = 'docu'
  docu2 = new Polygon 0.05
  docu2.start 1.0, 0.0
  docu2.add 3.0, 2.0, 40.0
  docu2.add 4.0, 0.0, -45.0
  docu2.add 3.0, -2.0, -40.0
  docu2.end 40.0
  docu2.type = 'docu'
  combine [docu1,docu2,silk1,silk2,silk3,silk4]
"""

eagle_polygon = """\
<package name="Polygon">
 <description>
  a simple polygon example
&lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 0aa9e2e2188f4b66a94f7e0f4b6bdded
 </description>
 <polygon layer="51" width="0.1">
  <vertex curve="180.0" x="0.0" y="1.0"/>
  <vertex curve="180.0" x="-1.0" y="0.0"/>
  <vertex curve="-10.0" x="0.0" y="-1.0"/>
  <vertex curve="-10.0" x="1.0" y="0.0"/>
 </polygon>
 <wire curve="180.0" layer="21" width="0.2" x1="1.41421356237" x2="-1.41421356237" y1="1.41421356237" y2="-1.41421356237"/>
 <polygon layer="51" width="0.05">
  <vertex curve="40.0" x="1.0" y="0.0"/>
  <vertex curve="-45.0" x="3.0" y="2.0"/>
  <vertex curve="-40.0" x="4.0" y="0.0"/>
  <vertex curve="40.0" x="3.0" y="-2.0"/>
 </polygon>
 <polygon layer="21" width="0.1">
  <vertex x="1.0" y="-4.0"/>
  <vertex x="-1.0" y="-4.0"/>
  <vertex curve="-90.0" x="-1.0" y="-3.0"/>
  <vertex curve="-70.0" x="-0.0" y="-2.0"/>
 </polygon>
 <polygon layer="21" width="0.05">
  <vertex x="1.1" y="1.2"/>
  <vertex x="1.1" y="0.2"/>
  <vertex x="0.1" y="1.2"/>
 </polygon>
 <wire curve="30.0" layer="21" width="0.075" x1="2.0" x2="1.0" y1="-1.0" y2="-0.5"/>
</package>"""
def test_eagle_export_polygon():
  with open('examples/0aa9e2e2188f4b66a94f7e0f4b6bdded.coffee') as f:
    hl_coffee = f.read()
  _export_eagle_package(hl_coffee, 'Polygon', eagle_polygon)

def test_eagle_import_one():
  def _eagle_do(d, mod):
    (code_list, item_list) = mod(*d)
    code_func = code_list[0]
    code_args = code_list[1:]
    code_text = code_func(*code_args)
    if code_args[0] == 'Smd':
      varname = 'smd1'
    else:
      varname = 'pad1'
    code = _one_coffee % (varname, code_text, varname)
    expected_code = _one_coffee % (varname, code_text, varname)
    item_func = item_list[0]
    item_args = item_list[1:]
    item_text = item_func(*item_args)
    eagle_xml = _one_coffee_eagle % (item_text)
    generated_code = _import_eagle_package(eagle_xml, 'TEST_EAGLE', expected_code)
  mods = [
    _no_mod, _mod_x, _mod_y, 
    partial(_mod_rotate, 90), partial(_mod_rotate, 180),
    partial(_mod_rotate, 270)
    ]
  # only do one test, as it fails currently anyway
  for mod in mods:
    for d in _one_coffee_tests:
      d2 = copy.deepcopy(d)
      yield _eagle_do, d2, mod

def test_eagle_import_polygon():
  expected_code = reimported_coffee_polygon
  _import_eagle_package(eagle_polygon, 'Polygon', expected_code)

empty_coffee = """\
#format 1.1
#name TEST_EMPTY
#id 708e13cc5f4e43f7833af53070ba5078
#desc coffee test
footprint = () ->
  combine []
"""

def test_eagle_export_empty():
  coffee = empty_coffee
  eagle = """\
<package name="TEST_EMPTY">
 <description>
  coffee test
&lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 708e13cc5f4e43f7833af53070ba5078
 </description>
</package>"""
  _export_eagle_package(coffee, 'TEST_EMPTY', eagle)

def test_kicad_export_empty():
  coffee = empty_coffee
  kicad = "(module TEST_EMPTY (layer F.Cu) (descr \"coffee test\"))"
  _export_kicad_package(coffee, 'TEST_EMPTY', kicad)

def test_kicad_import_empty():
  with open("test/kicad_empty.kicad_mod") as f:
    _import_kicad_package(f.read(), "TEST_EMPTY", empty_coffee)

kicad_polygon = """\
(module Polygon (layer F.Cu) (descr "a simple polygon example") (fp_poly (pts (xy 0 -1) (xy -1 0) (xy 0 1) (xy 1 0) (xy 0 -1)) (layer Dwgs.User) (width 0.1)) (fp_arc (start 0.0 -0.0) (end 1.41421356237 -1.41421356237) (angle -180.0) (layer F.SilkS) (width 0.2)) (fp_poly (pts (xy 1 0) (xy 3 -2) (xy 4 0) (xy 3 2) (xy 1 0)) (layer Dwgs.User) (width 0.05)) (fp_poly (pts (xy 1 4) (xy -1 4) (xy -1 3) (xy -0.0 2) (xy 1 4)) (layer F.SilkS) (width 0.1)) (fp_poly (pts (xy 1.1 -1.2) (xy 1.1 -0.2) (xy 0.1 -1.2) (xy 1.1 -1.2)) (layer F.SilkS) (width 0.05)) (fp_arc (start 0.566987298108 2.61602540378) (end 2.0 1.0) (angle -30.0) (layer F.SilkS) (width 0.075)))\
"""

def test_kicad_export_polygon():
  with open('examples/0aa9e2e2188f4b66a94f7e0f4b6bdded.coffee') as f:
    _export_kicad_package(f.read(), 'Polygon', kicad_polygon)

def test_kicad_import_polygon():
  expected_code = reimported_coffee_polygon
  _import_kicad_package(kicad_polygon, 'Polygon', expected_code)
