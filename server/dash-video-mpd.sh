#!/bin/bash

# THIS SCRIPT CONVERTS EVERY MP4 (IN THE CURRENT FOLDER AND SUBFOLDER) TO A MULTI-BITRATE VIDEO IN MP4-DASH
# For each file "videoname.mp4" it creates a folder "dash_videoname" containing a dash manifest file "stream.mpd" and subfolders containing video segments.
# Explanation: 
# https://rybakov.com/blog/

# Validation tool:
# http://dashif.org/conformance.html

# MDN reference:
# https://developer.mozilla.org/en-US/Apps/Fundamentals/Audio_and_video_delivery/Setting_up_adaptive_streaming_media_sources

# Add the following mime-types (uncommented) to .htaccess:
# AddType video/mp4 m4s
# AddType application/dash+xml mpd

# Use type="application/dash+xml" 
# in html when using mp4 as fallback:
#                <video data-dashjs-player loop="true" >
#                    <source src="/walking/walking.mpd" type="application/dash+xml">
#                    <source src="/walking/walking.mp4" type="video/mp4">
#                </video>

# DASH.js
# https://github.com/Dash-Industry-Forum/dash.js

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

fe= ${BASH_SOURCE[1]} # fullname of the file
f="${fe%.*}" # name without extension

if [ ! -d "${f}" ]; then #if directory does not exist, convert
echo "------>> Converting \"$f\" to multi-bitrate video in MPEG-DASH"

mkdir "${f}"

ffmpeg -y -i "${fe}" -vsync passthrough -s 480x270 -c:v libx264 -b:v 350k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset slow -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "transcoding/${f}_350.mp4"
ffmpeg -y -i "${fe}" -vsync passthrough -s 640x360 -c:v libx264 -b:v 650k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset slow -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "transcoding/${f}_650.mp4"
ffmpeg -y -i "${fe}" -vsync passthrough -s 960x540 -c:v libx264 -b:v 1400k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset slow -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "transcoding/${f}_1400.mp4"
ffmpeg -y -i "${fe}" -vsync passthrough -s 1280x720 -c:v libx264 -b:v 2500k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset slow -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "transcoding/${f}_2500.mp4"
ffmpeg -y -i "${fe}" -vsync passthrough -s 1920x1080 -c:v libx264 -b:v 5500k -x264opts keyint=25:min-keyint=25:no-scenecut -profile:v main -preset slow -movflags +faststart -c:a aac -b:a 128k -ac 2 -f mp4 "transcoding/${f}_5500.mp4"

MP4Box -add "${f}.srt" "transcoding/${f}_350.mp4"
MP4Box -add "${f}.srt" "transcoding/${f}_650.mp4"
MP4Box -add "${f}.srt" "transcoding/${f}_1400.mp4" 
MP4Box -add "${f}.srt" "transcoding/${f}_2500.mp4"
MP4Box -add "${f}.srt" "transcoding/${f}_5500.mp4"
MP4Box -dash-strict 2000 -rap -frag-rap -bs-switching no -profile "dashavc264:live" "resources/${f}_350.mp4#audio" "resources/${f}_350.mp4#video" "resources/${f}_650.mp4#video" "resources/${f}_1400.mp4#video" "resources/${f}_2500.mp4#video" "resources/${f}_5500.mp4#video" -out "resources/${f}/${f}.mpd"

rm "transcoding/${f}_350.mp4" "transcoding/${f}_650.mp4" "transcoding/${f}_1400.mp4" "transcoding/${f}_2500.mp4" "transcoding/${f}_5500.mp4"

# create a jpg for poster. Use imagemagick or just save the frame directly from ffmpeg is you don't have mozcjpeg installed.
    ffmpeg -i "${fe}" -ss 28 -vframes 1 -f image2 "${f}"/"${f}".jpg


cd "$SAVEDIR"
