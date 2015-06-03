#! /bin/bash

#epydoc -v -c style.css --parse-only -o scripts/ ../src/*.py
epydoc --no-frames -v -c elyxer.css --parse-only -o doc/ *.py
