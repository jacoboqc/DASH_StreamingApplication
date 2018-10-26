var path = require('path');
var formidable = require('formidable');
var fs = require('fs');
var request = require('request');
var express = require('express');
var app = express();
var log4js = require('log4js');

var AWS = require('aws-sdk');
log4js.configure({
    appenders: { 
        proxy: { type: 'file', filename: 'proxy.log' },
        console: { type: 'console' }
    },
    categories: { default: { appenders: ['proxy'], level: 'INFO' } }
});
const logger = log4js.getLogger('proxy');

// Create an S3 client
var myBucket = 'dash-cloud-website';
var queueName = 'test_queue';

var s3 = new AWS.S3();
var sqs = new AWS.SQS();

app.use('/', express.static('views'));
app.use('/resources', express.static('resources'));
app.use('/public', express.static('public'));
app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
  });


app.get('/', function (req, res) {
    res.sendFile(__dirname + '/views/index.html');
});


app.get('/video_player/:video', function (req, res) {
    video_path = 'http://s3-eu-west-1.amazonaws.com/' + myBucket + '/resources/' + req.params.video;
    res.header('Access-Control-Allow-Origin', '*');
    res.redirect(301, '/video_player.html?video=' + video_path + '/' + req.params.video + '.mpd');
});

app.get('/cover/:image', function (req, res) {
    
    image_path = 'http://s3-eu-west-1.amazonaws.com/' + myBucket + '/resources/' + req.params.image;
    request(image_path).pipe(res);
    //res.sendFile(image_path + '/' + req.params.image +'.jpg');
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
        logger.error(' An error has occured: \n' + err);
    });

    // once all the files have been uploaded, send a response to the client
    form.on('end', function () {
        res.end('success');
        saveFileToS3(filename);
    });

    // parse the incoming request containing the form data
    form.parse(req);
});

app.get('/videos', function (req, res) {
    var params = {
        Bucket: myBucket, 
        Prefix: 'resources/',
        StartAfter: 'resources/',
        Delimiter: 'm4s'
    };
    var files = [];
    listAllKeys();
    var i = 0;
    function listAllKeys(){
        s3.listObjectsV2(params, function(err, data) {
            if (err) {
                logger.error(err, err.stack); // an error occurred
            } else {
                var contents = data.Contents;
                contents.forEach(function (content) {
                    var key = content.Key.split("/")[1];
                    // compare element 2 of the routes, if they are the same do not add it to array.
                    if (files[files.length - 1] != undefined){
                        if (files[files.length - 1] != key)
                            files.push(content.Key);
                    }else{
                        files.push(key);
                    }
                });
            }
            logger.info(files);
            res.send(files);
        });
    }
});

app.post('/test', function (req, res) {
    //send to transconde 10 videos
    for(i = 0; i < 10; i++){
        video_path = 'http://s3-eu-west-1.amazonaws.com/' + myBucket + '/uploads/' + 'video_test' + i + '.mp4';
        sendQueueMessage(video_path);
    }
});

app.listen(8000, "0.0.0.0", function () {
    logger.info(' Server listening on port http://0.0.0.0:8000 !');
});

function saveFileToS3(filename) {
    var myKey = 'uploads/' + filename;
    var filePath = 'uploads/' + filename;
    var dataUrl = null;


    fs.readFile(filePath, function(err, data){
        if (err) {
            logger.error(' An error has occured: \n ' + err);
        } else {
            var params = {
                Bucket: myBucket,
                Key: myKey,
                Body: data
            };
            // upload file to S3
            s3.upload(params, function(s3Err, data) {
                if (s3Err) {
                    logger.error(' An error has occured in S3: \n ' + s3Err);
                } else
                    dataUrl = data.Location;
                    logger.info(' File uploaded successfully at ' + dataUrl);
            });
            // remove file from local disk
            fs.unlink(__dirname + filePath, (err) => {
                if (err) {
                    logger.info(' An error has occured: \n' + err);
                } else
                    logger.info(' ' + filePath + ' deleted.')
            });
        }
    });

    if (dataUrl != null){
        sendQueueMessage(dataUrl);
    }
}

function sendQueueMessage(dataUrl){
    var params = {
        QueueName: queueName
    };
    var queueUrl = null;

    sqs.getQueueUrl(params, function(err, data) {
        if (err) {
          logger.error("Error", err);
        } else {
          logger.info("Success", data.QueueUrl);
          queueUrl = data.QueueUrl
        }
      });

      if (queueUrl != null){
          body = {
              'fileUrl':  dataUrl
          };
          var params = {
            MessageBody: JSON.stringify(body),
            QueueUrl: queueUrl,
            DelaySeconds: 0 
          };

          sqs.sendMessage(params, function(err, data) {
            if (err) {
                logger.error(' An error has occured: \n ' + err);
              } else {
                logger.info(' Message sent to queue ' + queueName + ' - messageID: ' + data.MessageId);
              }
          });
      }
}
