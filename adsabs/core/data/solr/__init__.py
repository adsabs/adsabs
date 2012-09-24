
from .request import *
from .response import *
from .solrdoc import *

__all__ = [
    'SolrRequest',
    'SolrResponse',
    'SolrDocument',
    'SolrDocumentSet',
    'query',
    'get_document'
    ]

def query(q, **kwargs):
    req = SolrRequest(q, **kwargs)
    return req.get_response()

def get_document(id, **kwargs):
    req = SolrRequest(q="identifier:%s" % id, fl="*")
    resp = req.get_response()
    if resp.get_count() == 1:
        return resp.next()
