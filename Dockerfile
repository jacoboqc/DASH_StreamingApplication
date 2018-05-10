FROM ubuntu:14.04
MAINTAINER jacoboqc

ENV repo https://github.com/Guiamrey/DASH_StreamingApplication.git
ENV gpac https://download.tsi.telecom-paristech.fr/gpac/release/0.7.0/gpac_0.7.0_amd64.deb
ENV ffmpeg https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz

RUN apt-get update
RUN apt-get install -y wget gdebi git xz-utils
RUN wget $gpac
RUN gdebi --non-interactive gpac*
RUN wget $ffmpeg
RUN tar -xvf 'ffmpeg-git-64bit-static.tar.xz'
RUN ln -s /ffmpeg-git-20180429-64bit-static/ffmpeg /usr/bin/ffmpeg 
RUN rm ffmpeg-git-64bit-static.tar.xz
RUN wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash \
	&& [ -s $HOME/.nvm/nvm.sh ] \
	&& . $HOME/.nvm/nvm.sh \
	&& nvm install 8.11.1 \
	&& nvm alias default 8.11.1 \
	&& npm install formidable node-cmd express
RUN git clone $repo
RUN chmod +x /DASH_StreamingApplication/server/dash_video_mpd.sh

ENV PATH /bin/versions/node/v8.11.1/bin:$PATH

EXPOSE 8000/tcp
WORKDIR /DASH_StreamingApplication/server
ENTRYPOINT node app.js
