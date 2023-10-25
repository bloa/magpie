#!/bin/bash

shopt -s globstar

bash clean.sh
rsync --archive ../../../{examples,magpie,tests} .
for file in **/*.py;
do
    python3 magpie utils/python_to_xml $file > $file.xml
done
