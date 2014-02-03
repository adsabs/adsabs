#### requirements
* casperjs - http://casperjs.org/
* phantomjs - http://phantomjs.org/

#### how to run
```
python shell.py runserver &
casperjs test tests/casperjs --includes=tests/casperjs_inc.js --baseTestUrl=http://localhost:5000
```

