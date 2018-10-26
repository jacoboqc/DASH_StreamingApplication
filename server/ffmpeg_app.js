var express = require('express');
var app = express();
var fs = require('fs');
var exec = require('child_process').exec, child;
var AWS = require('aws-sdk');
var bodyParser = require('body-parser')

var myBucket = 'dash-cloud-website';
var s3 = new AWS.S3();

app.use( bodyParser.json() ); 

app.post('/accept_job', function (req, res) {
    
    var data = req.body.video;
    console.log('DATA RECEIVED IN POST ---> URL ---> ' + data);
    var data = data.split("/");
    var key = data[data.length - 2] + '/' + data[data.length - 1];
    console.log ('-----> '+ key);
    var params = {
        Bucket: myBucket, 
        Key: key
    };

    s3.getObject(params, function(err, data) {
        if (err) console.log(err, err.stack); 
        else {
            fs.writeFile(key, data.Body, (err) => {
                if (err) {
                    console.log('[ERROR] An error has occured: \n');
                    res.status(400);
                    res.send('ERROR');
                    throw err;
                } else
                    console.log('[INFO] File ' + key + ' written. Now transcoding.');
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
            console.log('GET time: No jobs running');
            res.send('0');
            return;
        } else {
            console.log('[INFO] Maximum time remaining is ' + stdout);
            res.send(stdout);
        }
    });
});

app.listen(8080, function () {
    console.log('Server listening on port 8080!');
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
            console.log('[ERROR] A error occured while executing ./dash-video-mpd.sh: ' + stderr);
            return;
        }    
    });
    script.on('close', (code) => {
        var path = url.split('/').pop();
        console.log('Transcoding finished. Uploading foler to S3 - PATH: ' + path);
        uploadFolderToS3(path)
    });
}
