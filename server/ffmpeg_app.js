var express = require('express');
var app = express();
var fs = require('fs');
var exec = require('child_process').exec, child;
var AWS = require('aws-sdk');

var myBucket = 'dash-cloud-website';
var s3 = new AWS.S3();

app.post('/accept_job', function (req, res) {
    
    var data = req.body.data;
    console.log('DATA RECEIVED IN POST ' + data);
    var key = data.video;
    console.log('DATA RECEIVED IN POST ---> URL ---> ' + key);

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
            })
        } 
    });
    
    transcoding(filename);
    
});

app.get('/time_remaining', function (req, res) {
    // TODO    
});

app.listen(8080, function () {
    console.log('Server listening on port 8000!');
});

function transcoding(filename) {
    var url = 'http://s3-eu-west-1.amazonaws.com/' + myBucket ;
    url = filename;
    command = './dash-video-mpd.sh ' + url // command to transcode files
    var testscript = exec(command);

    testscript.stdout.on('data', function (data) {
        console.log(data);
    });

    testscript.stderr.on('data', function (data) {
    });
}