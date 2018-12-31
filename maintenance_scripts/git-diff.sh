#!/bin/sh
git -c 'color.status=always' status | grep -v -e colors/ -e dumpster/ -e git-diff
