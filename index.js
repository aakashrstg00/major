const express = require('express');
const bodyParser = require('body-parser');
// var mongoose = require('mongoose');
var path = require('path');
var fs = require('fs');
var formidable = require('formidable');
var CsvReadableStream = require('csv-reader');
const app = express();

// mongoose.connect('mongodb://rastogi:rastogi1@ds121343.mlab.com:21343/cloudai');

app.use(express.static(path.join(__dirname, 'public')));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', (req, res) => {
    res.send({ hello: 'hola' });
});

app.post('/ml/image-classification', (req, res) => {
    var form = new formidable.IncomingForm();
    form.parse(req, (err, fields, files) => {
        console.log(files);
    });
});

app.post('/visualise', (req, res) => {
    var form = new formidable.IncomingForm();
    form.parse(req, function (err, fields, files) {
        if (files.csvfile) {
            fs.rename(files.csvfile.path, path.join(__dirname, './public/uploads/') + files.csvfile.name, function (err) {
                if (err) throw err;
                var inputStream = fs.createReadStream(path.join(__dirname, 'public/uploads/') + files.csvfile.name, 'utf8');
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
        }
        else {
            res.send({ error: 'File Not Found in Request', code: '' });
        }
    });
});

app.set('port', process.env.PORT || 7777);
app.listen(app.get('port'), () => {
    console.log('Server started at ' + app.get('port'));
});