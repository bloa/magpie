#!/usr/bin/env bash

patch triangle.c _magpie/triangle_bug.c.diff
#srcml triangle.c > _magpie/triangle_bug.c.xml
mv _magpie/triangle_bug.c.xml triangle.c.xml
