'''
Created on May 23, 2014

@author: jluker
'''
import re
import os
import sys
import shutil
import pexpect
import subprocess

from flask.ext.script import Manager, prompt, prompt_bool
from flask import current_app as app

from config import config

name = 'mongo'
manager = Manager("Mongo Operations", with_default_commands=False)

dbs = [
      { 'name': 'adsabs', 'passwd': config.MONGOALCHEMY_PASSWORD },
      { 'name': 'adsgut', 'passwd': re.search(':(?P<password>\w+)@', config.MONGODB_SETTINGS['HOST']).groupdict()['password'] },
      { 'name': 'adsdata', 'passwd': config.ADSDATA_MONGO_PASSWORD },
    ]

@manager.command
def backup(target, backup_dir=None, which_db=None, yes=False):
    """
    use mongodump to create backup dumps of all or individual databases
    
    Args:
        target(str): name of the dump directory / basename of the archive file
        backup_dir(str): path the final archive file will be copied to
        which_db(str): only backup this database
        yes(bool): say "y" to any prompts
        
    Example:
        shell.py mongo backup backup_20140604 /proj/ads_backups/mongodb
        
    """
    dumps = 0
    for db in dbs:
        db_name = db['name']
        db_passwd = db['passwd']
        if which_db is not None and which_db != db_name:
            app.logger.info("skipping %s", db_name)
            continue
        target_path = os.path.join(config.DATA_BACKUP_TMP_DIR, target)
        if not os.path.exists(target_path):
            if yes or prompt_bool("Target path %s does not exist. Create it?" % target_path):
                app.logger.info("creating target path %s", target_path)
                os.makedirs(target_path)
            else:
                app.logger.info("aborting backup")
                return
        app.logger.info("backing up %s to %s", db_name, target_path)
        
        # execute the dump
        dumps += 1
        cmd = "mongodump -u %s -o %s -d %s -p" % (db_name, target_path, db_name)
        child = pexpect.spawn(cmd, timeout=500000)
        idx = child.expect('password: ')
        if idx != 0:
            app.loggger.error("mongodump execution failed for db %s: %s" % (db_name, str(child)))
            dumps -= 1
            continue
        child.sendline(db_passwd)
        child.wait()
        child.close()
        
        if child.exitstatus is not 0:
            app.logger.error("mongodump returned non-zero exit status for db %s: %d" % (db_name, child.exitstatus))
            dumps -= 1
            continue
            
    if not dumps > 0:
        app.logger.info("No dumps created. Exiting.")
        return
    
    # now compress everything
    try:
        retcode = subprocess.call(["tar", 
                     "-C", config.DATA_BACKUP_TMP_DIR,
                     "-czf", target_path + ".tgz", 
                     target])
        if retcode != 0:
            app.logger.error("tar/compress returned non-zero status: %d" % retcode)
            return
    except OSError, e:
        app.logger.error("tar/compress execution failed: %s" % e)
    
    # remove the uncompressed dump
    try:
        retcode = subprocess.call(["rm", "-rf", target_path])
        if retcode != 0:
            app.logger.error("removal of target dir returned non-zero status: %d" % retcode)
            return
    except OSError, e:
        app.logger.error("removal of target dir failed: %s" % e)
        
    # move the compressed archive to it's final location
    if backup_dir is not None:
        try:
            compressed_path = target_path + ".tgz"
            if not os.path.exists or not os.path.isdir(backup_dir):
                raise OSError("backup_dir %s either doesn't exist or is not a directory" % backup_dir)
            shutil.move(compressed_path, backup_dir)
        except shutil.Error, e:
            app.logger.error("copy of compressed archive %s to %s failed: %s" % \
                                (compressed_path, backup_dir, e))
        
@manager.command
def rotate_backups(backup_dir, force=False):
    from tempfile import NamedTemporaryFile
    assert os.path.exists(backup_dir)
    with NamedTemporaryFile() as f:
        print >>f, "%s/*.tgz {\nrotate 7\ndaily\nmissingok\nnocreate\n}" % os.path.abspath(backup_dir)
        f.flush()
        force = force and "-f" or ""
        statefile = "%s/backup.state" % os.path.abspath(backup_dir)
        try:
            retcode = subprocess.call("logrotate %s -s %s -v %s" % (force, statefile, f.name), shell=True)
            if retcode != 0:
                app.logger.error("backup rotate command returned non-zero status: %d" % retcode)
                return
        except OSError, e:
                app.logger.error("backup rotate execution failed: %s" % e)
        
@manager.command
def restore(source, db):
    """
    use mongorestore to restore a previously dumped database
    """
    if db not in [x['name'] for x in dbs]:
        app.logger.error("I don't know anything about a database called %s", db)
        return
    if not os.path.exists(source):
        app.logger.error("Source path %s doesn't exist", source)
        return
    drop = prompt_bool("Drop existing collections before restoring?") and '--drop' or ''
    passwd = filter(lambda x: x['name'] == db, dbs)[0]['passwd']
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