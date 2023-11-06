#!/usr/bin/env bash

CACHE=$MAGPIE_ROOT/_magpie_cache

# download and cache archive
mkdir -p $CACHE
if ! test -f $CACHE/minisat-2.2.0.tar.gz; then
    wget "http://minisat.se/downloads/minisat-2.2.0.tar.gz"
fi
mv minisat-2.2.0.tar.gz $CACHE

# extract, patch, and setup pre-computed XML AST
tar xzf $CACHE/minisat-2.2.0.tar.gz --strip-components=1
patch core/Dimacs.h _magpie/dimacs.diff
# srcml core/Solver.cc > _magpie/Solver.cc.xml
mv _magpie/Solver.cc.xml core
