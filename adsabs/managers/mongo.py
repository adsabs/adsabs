'''
Created on May 23, 2014

@author: jluker
'''
import re
import os
import subprocess

from flask.ext.script import Manager, prompt, prompt_bool
from flask import current_app as app

from config import config

name = 'mongo'
manager = Manager("Mongo Operations", with_default_commands=False)

dbs = {
       'adsabs': config.MONGOALCHEMY_PASSWORD,
       'adsdata': config.ADSDATA_MONGO_PASSWORD,
       'adsgut': re.search(':(?P<password>\w+)@', config.MONGODB_SETTINGS['HOST']).groupdict()['password']
    }

@manager.command
def backup(target, which_db=None):
    """
    use mongodump to create backup dumps of all or individual databases
    """
    for db, passwd in dbs.items():
        if which_db is not None and which_db != db:
            app.logger.info("skipping %s", db)
            continue
        if not os.path.exists(target):
            if prompt_bool("Target path does not exist. Create it?"):
                app.logger.info("creating target path %s", target)
                os.makedirs(target)
            else:
                app.logger.info("aborting backup of %s", db)
        app.logger.info("backing up %s to %s", db, target)
        subprocess.call(["mongodump",
                         "-u", db,
                         "-p", passwd,
                         "-o", target,
                         "-d", db])

@manager.command
def restore(source, db):
    """
    use mongorestore to restore a previously dumped database
    """
    if db not in dbs:
        app.logger.error("I don't know anything about a database called %s", db)
        return
    if not os.path.exists(source):
        app.logger.error("Source path %s doesn't exist", source)
        return
    drop = prompt_bool("Drop existing collections before restoring?") and '--drop' or ''
    passwd = dbs[db]
    app.logger.info("Restoring %s database from %s" % (db, source))
    subprocess.call(["mongorestore", 
                     "-d", db,
                     "-u", db,
                     "-p", passwd,
                     drop,
                     source])
    
@manager.command
def migrate(migration_id):
    """
    execute a database "migration" script.
    migration scripts should be placed in the adsabs.migrations package. see format examples there.
    """
    def import_migration():
        package_path = 'migrations.migrate_%s' % migration_id
        m = __import__(package_path)
        # traverse the package path
        for n in package_path.split(".")[1:]:
            m = getattr(m, n)
        return m
    
    m = import_migration()
    m.migrate()