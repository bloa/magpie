#!/usr/bin/env bash

bash clean.sh
rsync --archive ../../../{examples,magpie,tests} .
