const express = require('express');
const bodyParser = require('body-parser');
// var mongoose = require('mongoose');
var path = require('path');
var fs = require('fs');
var formidable = require('formidable');
var CsvReadableStream = require('csv-reader');
const spawn = require("child_process").spawn;
const app = express();

// mongoose.connect('mongodb://rastogi:rastogi1@ds121343.mlab.com:21343/cloudai');

app.use(express.static(path.join(__dirname, 'public')));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});
app.get('/', (req, res, next) => {
    res.send({ hello: 'hola' });
    next();
});

app.post('/ml/image-classification/test', (req, res) => {
    var form = new formidable.IncomingForm();
    form.multiples = true;
    form.parse(req, (err, fields, files) => {
        console.log(files.images);
        var filePaths = [];
        files.images.forEach(image => {
            filePaths.push(image.path);
        });
        var p = spawn('python', [path.join(__dirname, '/ml-code/test.py'), JSON.stringify(filePaths)]);
        p.on('start', function (data) { res.send({ msg: data }); });
        p.on('end', data => {
            console.log('Ended process');
            fs.readFileSync(path.join(__dirname, 'ml-code/text-pred/result.json'), (err, data) => {
                if (err) throw err;
                console.log(data.toString());
            })
        })
    });
});

app.post('/ml/text-prediction/test', (req, res) => {

    // var p = spawn('python3', [path.join(__dirname, '/ml-code/text-predictor.py'), 'test', req.body.textdata]);
    // p.stdout.on('end', data => {
    //     console.log('Ended process');
    //     fs.readFileSync(path.join(__dirname, 'ml-code/text-pred/result.json'), (err, data) => {
    //         if (err) throw err;
    //         console.log(data.toString());
    //         // res.send({'text':'is'});
    //     })
    // });

    var arr = ['the','for','and','that','this','as','or']
    res.send(arr[Math.ceil(Math.random()*arr.length)]);
});

app.get('/visualise', (req, res) => {
    res.send('Use POST');
});

app.post('/visualise', (req, res) => {
    var form = new formidable.IncomingForm();
    form.parse(req, function (err, fields, files) {
        if (files.csvfile) {
            var oldpath = files.csvfile.path;
            var newpath = path.join(__dirname, './public/uploads/') + files.csvfile.name;
            fs.readFile(oldpath, (err, data) => {
                if (err) throw err;
                console.log('File read!');
                fs.writeFile(newpath, data, function (err) {
                    if (err) throw err;
                    var inputStream = fs.createReadStream(newpath, 'utf8');
                    var all_rows = [];
                    inputStream
                        .pipe(CsvReadableStream({ parseNumbers: true, parseBooleans: true, trim: true }))
                        .on('data', function (row) {
                            all_rows.push(row);
                        })
                        .on('end', function (data) {
                            var cdata = {
                                headers: all_rows[0],
                                data: all_rows.slice(1, all_rows.length - 1)
                            };
                            res.send(cdata);
                        });
                });
                // Delete the file
                fs.unlink(oldpath, function (err) {
                    if (err) throw err;
                    console.log('File deleted!');
                });
            });
        }
        else {
            res.send({ error: 'File Not Found in Request', code: '404' });
        }
    });
});

app.set('port', process.env.PORT || 7777);
app.listen(app.get('port'), () => {
    console.log('Server started at ' + app.get('port'));
});



var p = spawn('python', ['./text-predictor.py', 'test', 'For']);
