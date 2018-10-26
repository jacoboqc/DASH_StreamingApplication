#!/bin/bash
max_time=0
for filename in logs/*.log; do
    current_time="$(grep -Eo '[0-9][0-9][:][0-9][0-9][:][0-9][0-9][.][0-9][0-9]' $filename | tail -1)"
    duration="$(grep -Eo -m 1 '[0-9][0-9][:][0-9][0-9][:][0-9][0-9][.][0-9][0-9]' $filename)"
    s="$(tac $filename | grep -Eo -m 1 '[0-1][.][0-9][0-9]?[0-9]?x' $filename | tail -1)"
    speed=${s::-1}
    current_time="$(echo $current_time | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')"
    duration="$(echo $duration | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')"
    final_time="$(echo "$duration $current_time $speed" | awk '{print (($1-$2)/$3)}')"
    if [ $final_time \> $max_time ]; then
        max_time=$final_time
    fi
    echo $max_time
done