var express = require('express');
var app = express();
var fs = require('fs');
var exec = require('child_process').exec, child;
var AWS = require('aws-sdk');

var myBucket = 'dash-cloud-website';
var s3 = new AWS.S3();

app.post('/transcode', function (req, res) {
    
    var data = req.body.data;
    var key = data;

    const params = {
        Bucket: myBucket, 
        Key: key
    };

    s3.getObject(params, function(err, data) {
        if (err) console.log(err, err.stack); 
        else {
            fs.writeFile(key, data.Body, (err) => {
                if (err) {
                    console.log('[ERROR] An error has occured: \n');
                    throw err;
                } else
                    console.log('[INFO] File ' + key + ' written. Now transcoding.');
            })
        } 
    });

    transcoding(filename);
    res.send('success');
});

app.get('/time', function (req, res) {
    
});

app.listen(8080, function () {
    console.log('Server listening on port 8000!');
});

function transcoding(filename) {
    command = './dash-video-mpd.sh ' + 'uploads/' + filename // command to transcode files
    var testscript = exec(command);

    testscript.stdout.on('data', function (data) {
        console.log(data);
    });

    testscript.stderr.on('data', function (data) {
    });
}