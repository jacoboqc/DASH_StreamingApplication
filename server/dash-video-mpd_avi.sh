#!/bin/bash

# THIS SCRIPT CONVERTS EVERY MP4 (IN THE CURRENT FOLDER AND SUBFOLDER) TO A MULTI-BITRATE VIDEO IN MP4-DASH
# For each file "videoname.mp4" it creates a folder "dash_videoname" containing a dash manifest file "stream.mpd" and subfolders containing video segments.
# Explanation: 
# https://rybakov.com/blog/

tstart=`date +%s`

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


if [ ! -d "resources/${f}" ]; then #if directory does not exist, convert
    echo "------>> Converting \"$f\" to multi-bitrate video in MPEG-DASH"

    mkdir "resources/${f}"

    # video codec H.264 -c:v libx264  audio codec AAC -c:a aac
    #ffmpeg -y -i "${fe}" -vsync passthrough -s 480x270 -c:v libx264 -b:v 350k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset slow -movflags +faststart -c:a libopus -b:a 128k -ac 2 -f mp4 "tmp/${f}_350.mp4"

    ffmpeg -y -i "${fe}" -vsync passthrough -s 480x270 -c:v libvpx -quality good -cpu-used 0 -b:v 350k -preset slow -movflags +faststart -c:a libvorbis -b:a 128k -ac 2 -f webm "tmp/${f}_350.webm"
    ffmpeg -y -i "${fe}" -vsync passthrough -s 640x360 -c:v libvpx -quality good -cpu-used 0 -b:v 650k -preset slow -movflags +faststart -c:a libvorbis -b:a 128k -ac 2 -f webm "tmp/${f}_650.webm"
    ffmpeg -y -i "${fe}" -vsync passthrough -s 960x540 -c:v libvpx -quality good -cpu-used 0 -b:v 1400k -preset slow -movflags +faststart -c:a libvorbis -b:a 128k -ac 2 -f webm "tmp/${f}_1400.webm"
    ffmpeg -y -i "${fe}" -vsync passthrough -s 1280x720 -c:v libvpx -quality good -cpu-used 0 -b:v 2500k -preset slow -movflags +faststart -c:a libvorbis -b:a 128k -ac 2 -f webm "tmp/${f}_2500.webm"
    ffmpeg -y -i "${fe}" -vsync passthrough -s 1920x1080 -c:v libvpx -quality good -cpu-used 0 -b:v 5500k -preset slow -movflags +faststart -c:a libvorbis -b:a 128k -ac 2 -f webm "tmp/${f}_5500.webm"

    if [ -f "${fsrt}.srt" ]; then #if srt file exists, add captions
        echo "---> Adding subtitles to videos"
        MP4Box -add "${fsrt}.srt":lang=es "tmp/${f}_350.webm"
        MP4Box -add "${fsrt}.srt":lang=es "tmp/${f}_650.webm"
        MP4Box -add "${fsrt}.srt":lang=es "tmp/${f}_1400.webm" 
        MP4Box -add "${fsrt}.srt":lang=es "tmp/${f}_2500.webm"
        MP4Box -add "${fsrt}.srt":lang=es "tmp/${f}_5500.webm"

    fi

    MP4Box -dash-strict 2000 -rap -frag-rap -bs-switching no -profile "dashavc264:live" "tmp/${f}_350.webm#audio" "tmp/${f}_350.webm#video":role=subtitle "tmp/${f}_650.webm#video":role=subtitle  "tmp/${f}_1400.webm#video":role=subtitle  "tmp/${f}_2500.webm#video":role=subtitle  "tmp/${f}_5500.webm#video":role=subtitle  -out "resources/${f}"/"${f}.mpd"

    #rm "tmp/${f}_350.mp4" "tmp/${f}_650.mp4" "tmp/${f}_1400.mp4" "tmp/${f}_2500.mp4" "tmp/${f}_5500.mp4"

    # create a jpg for poster. Use imagemagick or just save the frame directly from ffmpeg is you don't have mozcjpeg installed.
    ffmpeg -i "${fe}" -ss 5 -vframes 1 -f image2 "resources/${f}"/"${f}".jpg

fi

cd "resources/${f}"
n="$(ls -afq | wc -l)"
c="$(($n - 2))"
if [ $c -eq 1 ]; then # if folder empty (errors occur) remove it
    cd "$SAVEDIR"
    rm -rf "resources/${f}"
fi

cd "$SAVEDIR"

tend=`date +%s`
runtime=$((tend-tstart))
echo "Execution time = "$runtime"ms"