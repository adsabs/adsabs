# ADSAbs 2.0

This is the Flask application for the new ADS website.

After making sure that you have python development files (package `python-dev` on debian-based systems) installed, the simple installation is:

    $ virtualenv some-python
    $ source some-python/bin/activate
    $ pip install -U pip
    $ pip install -U distribute
    $ CFLAGS= pip install -r requirements.txt

You will need a running mongodb instance. Assuming, you are just testing things, you can do:

    $ cat <<EOF> ./mongo_auth.js
    use admin
    db.addUser('foo','bar')
    db.auth('foo','bar')
    use adsabs
    db.addUser('adsabs','adsabs')
    use adsdata
    db.addUser('adsdata','adsdata')
    use adsgut
    db.addUser('adsgut','adsgut')
    EOF

    $ mongo < ./mongo_auth.js
   
Then, edit `config/local_config.py` and add:

    class LocalConfig(object):
        MONGOALCHEMY_USER = 'adsabs'
        MONGOALCHEMY_PASSWORD = 'adsabs'
        ADSDATA_MONGO_USER = 'adsdata'
        ADSDATA_MONGO_PASSWORD = 'adsdata'
        MONGODB_SETTINGS= {'HOST': 'mongodb://adsgut:adsgut@localhost/adsgut', 'DB': 'adsgut'}
        THUMBNAIL_MONGO_PASSWORD = None

For more details, see http://labs.adsabs.harvard.edu/trac/ads-invenio/wiki/BeerInstallation
or look into the Jenkins task, where we test the setup: [http://adswhy:9090/view/BEER/job/BEER-05-live-service/configure](http://adswhy:9090/view/BEER/job/BEER-05-live-service/configure)

## Jenkins

You can have Jenkins automatically test your repository/branch:

   1. got to adswhy:9090 (login)
   2. click on 'create a new job'
   3. select 'copy from' = BEER-02-adsabs
   4. change some values:
      - the git url (and optionally the name of the branch you want to test)
      - port of a mongo db (MongoDB is created for each test, so you just want to avoid using a port that some other tests use)
      - email (to notify you of build problems)
   
