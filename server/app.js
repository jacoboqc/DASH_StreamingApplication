var path = require('path');
var formidable = require('formidable');
var fs = require('fs');
var express = require('express');
var app = express();
var exec = require('child_process').exec,
    child;
var AWS = require('aws-sdk');

// Create an S3 client
var myBucket = 'dash-cloud-website';

var s3 = new AWS.S3();


app.use('/', express.static('views'));
app.use('/resources', express.static('resources'));
app.use('/public', express.static('public'));


app.get('/', function (req, res) {
    res.sendFile(__dirname + '/views/index.html');
});


app.get('/video_player/:video', function (req, res) {
    video_path = '/resources/' + req.params.video;
    res.redirect(301, '/video_player.html?video=' + video_path + '/' + req.params.video + '.mpd');
});

app.get('/cover/:image', function (req, res) {
    res.sendFile(__dirname + '/resources/' + req.params.image + '/' + req.params.image +'.jpg');
});

app.post('/upload', function (req, res) {

    var filename;
    // create an incoming form object
    var form = new formidable.IncomingForm();

    // specify that we want to allow the user to upload multiple files in a single request
    form.multiples = true;

    // store all uploads in the /uploads directory

    form.uploadDir = path.join(__dirname, '/uploads');

    // every time a file has been uploaded successfully,
    // rename it to it's orignal name
    form.on('file', function (field, file) {
        filename = file.name;
        fs.rename(file.path, path.join(form.uploadDir, file.name));
    });

    // log any errors that occur
    form.on('error', function (err) {
        console.log('[ERROR] An error has occured: \n' + err);
    });

    // once all the files have been uploaded, send a response to the client
    form.on('end', function () {
        res.end('success');
        saveFileToS3(filename);
       // transcoding(filename);
    });

    // parse the incoming request containing the form data
    form.parse(req);
});

app.get('/videos', function (req, res) {
    fs.readdir('resources', (err, files) => {
        res.send(files);
    })
});

app.post('/test', function (req, res) {
    // TODO
});

app.listen(8000, function () {
    console.log('[INFO] Server listening on port 8000!');
});

function saveFileToS3(filename) {
    var myKey = 'uploads/' + filename;
    var filePath = 'uploads/' + filename;

    fs.readFile(filePath, function(err, data){
        if (err) {
            console.log('[ERROR] An error has occured: \n');
            throw err;
        } else {
            const params = {
                Bucket: myBucket,
                Key: myKey,
                Body: data
            };
            // upload file to S3
            s3.upload(params, function(s3Err, data) {
                if (s3Err) {
                    console.log('[ERROR] An error has occured in S3: \n');
                throw s3Err;
                } else
                    console.log('[INFO] File uploaded successfully at ${data.Location}');
            });
            // remove file from local disk
            fs.unlink(__dirname + filePath, (err) => {
                if (err) {
                    console.log('[ERROR] An error has occured: \n');
                    throw err;
                } else
                    console.log('[INFO] ' + filePath + ' deleted.')
            });
        }
    });
}

// function transcoding(filename) {
//     command = './dash-video-mpd.sh ' + 'uploads/' + filename // command to transcode files
//     var testscript = exec(command);

//     testscript.stdout.on('data', function (data) {
//         console.log(data);
//     });

//     testscript.stderr.on('data', function (data) {
//     });
// }
