#!/usr/bin/env bash

CACHE=$MAGPIE_ROOT/_magpie_cache
ARCHIVE=minisat-2.2.0.tar.gz

# download and cache archive
mkdir -p $CACHE
if ! test -f $CACHE/$ARCHIVE; then
    wget "http://minisat.se/downloads/$ARCHIVE"
    mv $ARCHIVE $CACHE
fi

# extract, patch, and setup pre-computed XML AST
tar xzf $CACHE/$ARCHIVE --strip-components=1
patch core/Dimacs.h _magpie/dimacs.diff
# srcml core/Solver.cc > _magpie/Solver.cc.xml
cp _magpie/Solver.cc.xml core
