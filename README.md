# DASH_StreamingApplication

## Deployment

Install [Docker](https://www.docker.com/) and then run

```sh
docker build . -t irac/dash
docker run -itp 80:8000/tcp irac/dash
```

The web interface is now up on [localhost](http://localhost). Ctrl-C to stop.
