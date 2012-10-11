
import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask.ext.script import Manager, Command, Option #@UnresolvedImport

from adsabs import create_app
from config import config
manager = Manager(create_app(config))

from adsabs.core.data import mongo

class Sync(Command):
    """
    updates the mongo data collections from their data source files
    """
    
    def run(self, collection=None, force=False, debug=False):
        for model_class in mongo.data_models():
            if collection and collection != model_class.config_collection_name:
                print "skipping %s" % model_class.config_collection_name
                continue
            if model_class.needs_sync() or force:
                model_class.load_data(batch_size=config.MONGO_DATA_LOAD_BATCH_SIZE)
            else:
                print "%s does not need syncing" % model_class.config_collection_name
        
    def get_options(self):
        return [
            Option('-f','--force', dest="force", type=bool, default=False),
            Option('-d','--debug', dest="debug", type=bool, default=False),
            Option('-c','--collection', dest="collection", type=str),
            ]
        
class Status(Command):
    """
    reports on update status of mongo data collections
    """
    
    def run(self, collection=None, debug=False):
        for model_class in mongo.data_models():
            print "%s needs sync? : %s" % (model_class.config_collection_name, model_class.needs_sync())
    
    def get_options(self):
        return [
            Option('-d','--debug', dest="debug", type=bool, default=False),
            ]
        
manager.add_command('sync', Sync())
manager.add_command('status', Status())

if __name__ == "__main__":
    manager.run()

