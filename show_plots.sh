#/bin/bash

if [ "$1" = 'immediate' ]; then
    immediate=true
elif [ -z "$1" ]; then
    immediate=false
else
    echo invalid option
    exit 1
fi

date -Is >> use_omicron.txt
cd "$HOME"/projects/time_tracker_omicron
if $immediate; then
    eog -f "$HOME"/projects/time_tracker_omicron/plots/ &
fi
ipython3 fetcher.ipynb
if ! $immediate; then
    eog -f "$HOME"/projects/time_tracker_omicron/plots/ &
fi
