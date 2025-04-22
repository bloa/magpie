#!/usr/bin/env bash

patch triangle.py _magpie/triangle_slow.diff
cp _magpie/triangle_slow.py.xml triangle.py.xml
