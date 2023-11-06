#!/usr/bin/env bash

patch triangle.c _magpie/triangle_slow.c.diff
patch triangle.h _magpie/triangle_slow.h.diff
#srcml triangle.c > _magpie/triangle_slow.c.xml
mv _magpie/triangle_slow.c.xml triangle.c.xml
