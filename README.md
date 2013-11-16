ADSAbs 2.0
=======

This is the Flask application for the new ADS website.

The simple installation is:

   $ virtualenv some-python
   $ source some-python/bin/activate
   $ pip install -U pip
   $ pip install -U distribute
   $ pip install -r requirements.txt


For more details, see http://labs.adsabs.harvard.edu/trac/ads-invenio/wiki/BeerInstallation


You can have Jenkins automatically test your repository/branch:

   1. got to adswhy:9090 (login)
   2. click on 'create a new job'
   3. select 'copy from' = BEER-02-adsabs
   4. change some values:
      - the git url (and optionally the name of the branch you want to test)
      - port of a mongo db (MongoDB is created for each test, so you just want to avoid using a port that some other tests use)
      - email (to notify you of build problems)
   
