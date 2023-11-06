#!/usr/bin/env bash

patch Triangle.java _magpie/TriangleBug.diff
#srcml Triangle.java > _magpie/TriangleBug.java.xml
mv _magpie/TriangleBug.java.xml Triangle.java.xml
