
import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask.ext.script import Manager, Command, Option #@UnresolvedImport

from multiprocessing import Pool, current_process

from adsabs import create_app
from config import config
manager = Manager(create_app(config))

import logging
log = None

from adsabs.core.data import mongo

def load_data(model_class):
    log.debug("thread '%s' working on %s" % (current_process().name, model_class))
    model_class.load_data(batch_size=config.MONGO_DATA_LOAD_BATCH_SIZE)
    
class Sync(Command):
    """
    updates the mongo data collections from their data source files
    """
    
    def run(self, collection, threads, force, debug):
        if debug:
            log.setLevel(logging.DEBUG)
        updates = []
        for model_class in mongo.data_models():
            if collection and collection != model_class.config_collection_name:
                log.info("skipping %s" % model_class.config_collection_name)
                continue
            if model_class.needs_sync() or force:
                updates.append(model_class)
            else:
                log.info("%s does not need syncing" % model_class.config_collection_name)
        if threads > 0:
            p = Pool(threads)
            p.map(load_data, updates)
        else:
            for cls in updates:
                load_data(cls)
        
    def get_options(self):
        return [
            Option('-c','--collection', dest="collection", type=str, default=None),
            Option('-t','--threads', dest="threads", type=int, default=4),
            Option('-f','--force', dest="force", type=bool, default=False),
            Option('-d','--debug', dest="debug", type=bool, default=False),
            ]
        
class Status(Command):
    """
    reports on update status of mongo data collections
    """
    
    def run(self, collection=None, debug=False):
        if debug:
            log.setLevel(logging.DEBUG)
        for model_class in mongo.data_models():
            log.info("%s needs sync? : %s" % (model_class.config_collection_name, model_class.needs_sync()))
    
    def get_options(self):
        return [
            Option('-d','--debug', dest="debug", type=bool, default=False),
            ]
        
manager.add_command('sync', Sync())
manager.add_command('status', Status())

if __name__ == "__main__":
    log = logging.getLogger()
    manager.run()

