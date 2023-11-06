#!/usr/bin/env bash

patch triangle.py _magpie/triangle_bug.diff
python3 ../../../magpie python_to_xml triangle.py > triangle.py.xml
