#!/bin/bash
cd $(dirname -- "$( readlink -f -- "$0"; )")
ipython3 server.ipynb