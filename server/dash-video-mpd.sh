#!/bin/bash

tstart="$(date "+%s")"

MYDIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
SAVEDIR=$(pwd)

# Check programs
if [ -z "$(which ffmpeg)" ]; then
    echo "Error: ffmpeg is not installed"
    exit 1
fi

if [ -z "$(which MP4Box)" ]; then
    echo "Error: MP4Box is not installed"
    exit 1
fi

cd "$MYDIR"

fe="$1" # fullname of the file 
f="${fe%.*}" # name without extension (with path)
fsrt="${f}"
f="${f##*/}" #remove path, just the name of the file
f="${f,,}"

if [ ! -d "resources" ]; then
    mkdir "resources"
    
if [ ! -d "resources/${f}" ]; then #if directory does not exist, convert

    mkdir "resources/${f}"

    ffmpeg -y -i "${fe}" -vsync passthrough \
    -s 426x240 -c:v libx264 -b:v 350k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset medium -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "tmp/${f}_350.mp4" \
    -s 640x360 -c:v libx264 -b:v 650k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset medium -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "tmp/${f}_650.mp4" \
    -s 854x480 -c:v libx264 -b:v 1400k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset medium -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "tmp/${f}_1400.mp4" \
    -s 1280x720 -c:v libx264 -b:v 3000k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset medium -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "tmp/${f}_2500.mp4" \
    -s 1920x1080 -c:v libx264 -b:v 5500k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset medium -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "tmp/${f}_5500.mp4" \
    2> "logs/${f}.log"
    
    tend="$(date "+%s")"
    runtime1="$(($tend - $tstart))"
    echo " ---->>> Execution time (ffmpeg) = "$runtime1" s"

    MP4Box -dash-strict 2000 -rap -frag-rap -bs-switching no -profile "dashavc264:live" "tmp/${f}_350.mp4#audio" "tmp/${f}_350.mp4#video" "tmp/${f}_650.mp4#video" "tmp/${f}_1400.mp4#video" "tmp/${f}_2500.mp4#video" "tmp/${f}_5500.mp4#video" -out "resources/${f}"/"${f}.mpd"

    rm "tmp/${f}_350.mp4" "tmp/${f}_650.mp4" "tmp/${f}_1400.mp4" "tmp/${f}_2500.mp4" "tmp/${f}_5500.mp4"

    # create a jpg for poster. Use imagemagick or just save the frame directly from ffmpeg is you don't have mozcjpeg installed.
    ffmpeg -i "${fe}" -ss 5 -vframes 1 -f image2 "resources/${f}"/"${f}".jpg

else
    echo "ERROR: Directory resources/${f} already exists. Exiting without doing anything."
fi

cd "resources/${f}"
n="$(ls -afq | wc -l)"
c="$(($n - 2))"
if [ $c -eq 1 ]; then # if folder empty (errors occur) remove it
    cd "$SAVEDIR"
    rm -rf "resources/${f}"
fi

cd "$SAVEDIR"

tend="$(date "+%s")"
runtime="$(($tend - $tstart))"
rm "logs/${f}.log"
echo "Total execution time = "$runtime" s" # execution time in milis