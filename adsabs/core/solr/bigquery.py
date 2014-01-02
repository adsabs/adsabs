'''
Created on Jan 2, 2014

@author: jluker
'''
import uuid
import pytz
from datetime import datetime
from adsabs.extensions import mongodb
from flask.ext.mongoalchemy import document #@UnresolvedImport

class BigQuery(mongodb.Document): #@UndefinedVariable
    """
    Model for the local database of ADS users
    """
    config_collection_name = 'big_query'
    
    #fields
    query_id = mongodb.StringField() #@UndefinedVariable
    data = mongodb.StringField() #@UndefinedVariable
    created = mongodb.DateTimeField(default=datetime.utcnow().replace(tzinfo=pytz.utc)) #@UndefinedVariableo
    
    # indexes
    query_id_index = document.Index().descending('query_id').unique()
    
def retrieve_bigquery(query_id):
    cursor = BigQuery.query.filter(BigQuery.query_id==query_id) #@UndefinedVariable
    query = cursor.first()
    if query is None:
        return None
    return query.data

def save_bigquery(data):
    # save data inside mongo and get unique id
    qid = str(uuid.uuid4())
    new_rec = BigQuery(
                query_id=qid,
                created=datetime.utcnow().replace(tzinfo=pytz.utc),
                data=data)
    new_rec.save()
    return qid

def prepare_bigquery_request(req, bigquery_id):
    bq_data = retrieve_bigquery(bigquery_id)
    if bq_data is not None:
        req.headers = {'content-type': 'big-query/csv'}
        req.data=bq_data
        req.add_filter_query('{!bitset}')
                