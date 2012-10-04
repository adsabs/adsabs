
from adsabs.core.data import mongo
from optparse import OptionParser

def main(opts):
    
    for model_class in mongo.data_models():
        collection_name = model_class.collection_name
        
    
if __name__ == '__main__':
    op = OptionParser()
    op.set_usage("usage: load_data_sources.py [options] ")
    op.add_option('--verbose', dest='verbose', action='store_true',
        help='write log output to stdout', default=False)
    op.add_option('--debug', dest='debug', action='store_true',
        help='include debugging info in log output', default=False)
    op.add_option('--force', dest='force', action='store_true',
        help='ignore modtimes', default=False)
    op.add_option('--status', dest='status', action='store_true',
        help='just check status of data freshness', default=False)
    op.add_option('--collection', dest='collection', action='store',
        help='load only this collection') 
    
    (opts, args) = op.parse_args()
    
    main(opts)