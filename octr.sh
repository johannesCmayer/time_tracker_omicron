#!/bin/bash
cd $(dirname -- "$( readlink -f -- "$0"; )")
date -Is >> usages.txt
python octr.py $@