#!/usr/bin/env bash

patch triangle.cpp _magpie/triangle_bug.cpp.diff
#srcml triangle.cpp > _magpie/triangle_bug.cpp.xml
mv _magpie/triangle_bug.cpp.xml triangle.cpp.xml
