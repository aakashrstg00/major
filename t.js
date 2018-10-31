var PythonShell = require('python-shell').PythonShell;
 var path = require('path')
PythonShell.run(path.join(__dirname,'/ml-code/text-pred/text-predictor.py'), {
    args: ['test','is']
}, function (err,r) {
  if (err) throw err;
  console.log(r);
});
