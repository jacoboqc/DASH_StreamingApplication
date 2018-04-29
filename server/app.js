var path = require('path');
var formidable = require('formidable');
var fs = require('fs');
var express = require('express');
var app = express();
var cmd = require('node-cmd');

app.use('/', express.static('views'));
app.use('/resources', express.static('resources'));
app.use('/public', express.static('public'));


app.get('/', function (req, res) {
    res.sendFile(__dirname + '/public/index.html');
});


app.get('/video_player/:video', function (req, res){
    console.log('Requesting ' + req.params.video);
    video_path = '/resources/' + req.params.video;
    res.redirect(301, '/video_player.html?video=' + video_path + '/' + req.params.video + '.mpd');
});


app.post('/upload', function (req, res) {

    // create an incoming form object
    var form = new formidable.IncomingForm();

    // specify that we want to allow the user to upload multiple files in a single request
    form.multiples = true;

    // store all uploads in the /uploads directory
    form.uploadDir = path.join(__dirname, '/uploads');

    console.log(form.uploadDir)
    // every time a file has been uploaded successfully,
    // rename it to it's orignal name
    form.on('file', function (field, file) {
        fs.rename(file.path, path.join(form.uploadDir, file.name));
    });

    // log any errors that occur
    form.on('error', function (err) {
        console.log('An error has occured: \n' + err);
    });

    // once all the files have been uploaded, send a response to the client
    form.on('end', function () {
        res.end('success');
    });

    // parse the incoming request containing the form data
    form.parse(req);
});

app.get('/videos', function(req, res){
    fs.readdir('resources', (err, files) => {
        res.send(files);
    })
});

app.listen(8000, function () {
    console.log('Server listening on port 8000!');
});

fs.watch('uploads/', (event, filename) => {
    command = './dash-video-mpd.sh ' + filename // command to transcode files

    cmd.get(command, (err, data, stderr) => {
            console.log('the current working dir is : ', data)
        }
    );
})

