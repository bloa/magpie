#!/bin/bash

shopt -s globstar

bash clean.sh
rsync --archive ../../../{examples,magpie,utils} .
for file in **/*.py;
do
    python3 utils/python_to_xml.py $file > $file.xml
done
