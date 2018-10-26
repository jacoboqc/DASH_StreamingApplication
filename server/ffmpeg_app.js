var express = require('express');
var app = express();
var fs = require('fs');
var exec = require('child_process').exec, child;
var AWS = require('aws-sdk');
var bodyParser = require('body-parser')
var log4js = require('log4js');

var myBucket = 'dash-cloud-website';
var s3 = new AWS.S3();

log4js.configure({
    appenders: { 
        ffmpeg: { type: 'file', filename: 'server.log' },
        console: { type: 'console' }
    },
    categories: { default: { appenders: ['ffmpeg'], level: 'INFO' } }
});
const logger = log4js.getLogger('ffmpeg');

app.use( bodyParser.json() ); 

app.post('/accept_job', function (req, res) {
    
    var data = req.body.video;
    logger.info('DATA RECEIVED IN POST ---> URL ---> ' + data);
    var data = data.split("/");
    var key = data[data.length - 2] + '/' + data[data.length - 1];
    logger.info ('-----> '+ key);
    var params = {
        Bucket: myBucket, 
        Key: key
    };

    s3.getObject(params, function(err, data) {
        if (err) logger.info(err, err.stack); 
        else {
            fs.writeFile(key, data.Body, (err) => {
                if (err) {
                    logger.error(' An error has occured: \n');
                    res.status(400);
                    res.send('ERROR');
                    throw err;
                } else
                    logger.info(' File ' + key + ' written. Now transcoding.');
                    res.status(200);
                    res.send('SUCCESS');
                    transcoding(key);
            })
        } 
    });
    
});

app.get('/time_remaining', function (req, res) {
    command = './time.sh'
    var script = exec(command, (error, stdout, stderr) => {
        if (error){
            logger.info('GET time: No jobs running');
            res.send('0');
            return;
        } else {
            logger.info(' Maximum time remaining is ' + stdout);
            res.send(stdout);
        }
    });
});

app.listen(8080, "0.0.0.0", function () {
    logger.info('Server listening on port http://0.0.0.0:8080/ !');
});

function uploadFolderToS3(videoname){
    command = 'aws s3 sync resources/' + videoname + ' s3://' + myBucket + '/resources';
    exec(command);
}

function transcoding(filename) {
    var url = 'http://s3-eu-west-1.amazonaws.com/' + myBucket ;
    url = filename;
    command = './dash-video-mpd.sh ' + url // command to transcode files
    var script = exec(command , (error, stdout, stderr) => {
        if (stderr){
            logger.error(' A error occured while executing ./dash-video-mpd.sh: ' + stderr);
            return;
        }    
    });
    script.on('close', (code) => {
        var path = url.split('/').pop();
        logger.info('Transcoding finished. Uploading foler to S3 - PATH: ' + path);
        uploadFolderToS3(path)
    });
}
