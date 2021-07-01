#!/bin/bash
mkdir ./tmp-1
mkdir ./trash
find . -type f | grep "violation-true" | cut -c 63- | parallel "find . -type f | grep {} | parallel mv -t ./tmp-1"
find . -maxdepth 1 -type f | parallel mv -t trash
find ./tmp-1 -type f | parallel mv -t .
rmdir tmp-1
