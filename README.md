Please remark that a rewrite in rust is in progress at https://github.com/rustit-be/madparts-rs

madparts
========

A functional footprint editor.

what's new in 2.0
=================

Library management functionality has been completely removed from madparts simplifying the workflow by just leaving it to the user and the filesystem and filenames. More details are available in the updated documentation.

features
========

* a footprint is a small program, giving you huge expressiveness
* import from, export to eagle cad and kicad libraries
* high level pattern detection for single, dual quad formations of pads
* instant graphical feedback with continuous compilation process
* easy collaboration because footprints are separate files and libraries are just directories

documentation
=============

Please check out the [website](http://madparts.org).

source dependencies
===================

* python (tested with 2.7)
* numpy (tested with 1.6.2)
* pyside (tested with 1.1.1)
* python-opengl (tested with 3.0.1)
* beautiful soup 4 (tested with 4.1.0)
* python-imaging (tested with 1.1.7)

Requires openGL 2.1 available on the display.

Detailed build instructions can be found in the source tree.
