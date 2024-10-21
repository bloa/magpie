#!/usr/bin/env bash

shopt -s globstar

# clean up just in case
bash clean.sh

# the relative magpie root is different when executed manually from "example/magpie"
parent_dir=$(basename "$(dirname "$(pwd)")")
if [ "$parent_dir" == "examples" ]; then
    rsync --archive ../../{examples,magpie,tests} .
    else
    rsync --archive ../../../{examples,magpie,tests} .
fi

# store the AST of every file
for file in **/*.py; do
    python3 magpie utils/python_to_xml $file > $file.xml
done
