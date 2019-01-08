#!/bin/bash

# Dead simple implementation for timetracking.

CONFIG="$HOME/.config/timetrack/config"

if [ -e $CONFIG ]; then
    source $CONFIG
else
    echo "No config file loaded. Exiting."
    exit 1
fi

time_now="$(date '+%s')"

if [ ! -z $@ ]; then
    activity=$1
    line="$time_now\t$activity"
elif [ ! -z $TT_DEFAULT_ACTIVITY ]; then
    line="$time_now\t$TT_DEFAULT_ACTIVITY"
elif [ -e $TT_FILE ]; then
    # The user probably wants to see what they did
    # Maybe include a thing to print the time as a user-readable time?
    # I just don't know how I would do that in bash.
    tail $TT_FILE
else
    echo "No file, no activity, don't know what to do."
fi

if [ ! -z $line ]; then
    echo -e $line | tee -a $TT_FILE
fi

