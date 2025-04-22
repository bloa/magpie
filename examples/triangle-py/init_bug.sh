#!/usr/bin/env bash

patch triangle.py _magpie/triangle_bug.diff
cp _magpie/triangle_bug.py.xml triangle.py.xml
