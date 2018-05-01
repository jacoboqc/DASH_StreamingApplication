FROM ubuntu:14.04
MAINTAINER jacoboqc

ENV repo https://github.com/Guiamrey/DASH_StreamingApplication.git
ENV gpac https://download.tsi.telecom-paristech.fr/gpac/release/0.7.0/gpac_0.7.0_amd64.deb

RUN apt-get update
RUN apt-get install -y software-properties-common wget gdebi git
RUN add-apt-repository -y ppa:mc3man/trusty-media \ 
	&& apt-get update && apt-get install -y ffmpeg
RUN wget $gpac
RUN gdebi --non-interactive gpac*
RUN wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash \
	&& [ -s $HOME/.nvm/nvm.sh ] \
	&& . $HOME/.nvm/nvm.sh \
	&& nvm install 8.11.1 \
	&& nvm alias default 8.11.1 \
	&& npm install formidable node-cmd express
RUN git clone $repo

ENV PATH /bin/versions/node/v8.11.1/bin:$PATH

EXPOSE 8000/tcp
WORKDIR /DASH_StreamingApplication/server
ENTRYPOINT node app.js
