#!/usr/bin/env bash

patch triangle.cpp _magpie/triangle_slow.cpp.diff
patch triangle.hpp _magpie/triangle_slow.hpp.diff
#srcml triangle.cpp > _magpie/triangle_slow.cpp.xml
mv _magpie/triangle_slow.cpp.xml triangle.cpp.xml
