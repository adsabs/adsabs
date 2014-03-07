'''
Restore from a mongo database dump and samples it, then creates *_stubb'd mongo dbs
'''

import pymongo
import subprocess
import random

def mongorestore(path):
  P = subrocess.Popen(['mongorestore',path])
  P.wait()

def sample(collection,fraction=0.1,min_sampled=10):
  sampled = []
  c = collection.count()
  for i in range(min(min_sampled,int(c*fraction))):
    sampled.append(collection.find().limit(-1).skip(random.randint(0,c-1)).next())
  return sampled


def mongorestore_stubbed_data(path):
  pass

def create_stubbed_data():
  client = pymongo.MongoClient()

  databases = {
    'adsdata':'/media/usbdisk/adsdata_Thu/adsdata',
    'adsgut':'/media/usbdisk/adsgut_Thu/adsgut',
    'adsabs':'/media/usbdisk/adsabs_Thu/adsabs',
  }

  for k,v in databases.iteritems():
    output_database = "%s_stub" % k
    if client[output_database].collection_names(): #Skip this whole process if _stub databases already are exist
      continue

    if not client[k].collection_names(): #Only restore if we dont already have the database up
      mongorestore(v)

    db = client[k]
    for collection in db.collection_names():
      for data in sample(db[collection]):
        client[output_database][collection].insert(data)


if __name__ == '__main__':
  main()