var express = require('express');
var bodyparser = require('body-parser');
var urlencodedParser = bodyparser.urlencoded({extended: true});
const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',["bitmexbot.py"]); // run python script
var app = express(); // set up an express app, gives us all functions of express
app.listen(8081);
app.set('view engine', 'ejs');
app.use(express.static('./public'));
console.log("Listening to port 8081");
app.get('/', function(req, res){ // express has extended these fucntion
    res.render('mainview');
});