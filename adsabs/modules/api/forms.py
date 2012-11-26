'''
Created on Sep 19, 2012

@author: jluker
'''

import re

from flask import g
from flask.ext.wtf import Form, fields as fields_, validators, ValidationError #@UnresolvedImport

from adsabs.core.solr import SolrRequest
from .renderers import VALID_FORMATS
from config import config

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 2048
SORT_DIRECTIONS = ['asc','desc']

def validate_q(form, field):
    """
    just checks for min/max length so far
    TODO: maybe do closer inspection of the query syntax?
    """
    if not len(field.data):
        return
    if len(field.data) < MIN_QUERY_LENGTH:
        raise ValidationError("'q' input must be at least %s characters" % MIN_QUERY_LENGTH)
    if len(field.data) > MAX_QUERY_LENGTH:
        raise ValidationError("'q' input must be at no more than %s characters" % MAX_QUERY_LENGTH)
        
class ApiQueryForm(Form):
    dev_key = fields_.TextField('dev_key', [validators.Required()])
    flds = fields_.TextField('fields')
    fmt = fields_.TextField('format')
    hl = fields_.FieldList(fields_.TextField('hl'))
    q = fields_.TextField('query', [validate_q])
    rows = fields_.IntegerField('rows')
    start = fields_.IntegerField('start')
    sort = fields_.TextField('sort')
    facet = fields_.FieldList(fields_.TextField('facet'))
    filter = fields_.FieldList(fields_.TextField('filter'))
    hlq = fields_.TextField('hlq', [validate_q])

    def validate_flds(self, field):
        """
        checks that input is a comma separated list of field names
        """
        if not len(field.data):
            return
        if re.search('[^a-z\.\_]', field.data, re.I):
            raise ValidationError("Invalid field selection: value must be a comma-separated (no whitespace) list of field names")
        for field in field.data.split(','):
            if field not in config.API_SOLR_FIELDS:
                raise ValidationError("Invalid field selection: %s is not a selectable field" % field)
    
    def validate_fmt(self, field):
        if not len(field.data):
            return
        if field.data not in VALID_FORMATS:
            raise ValidationError("Invalid format: %s. Valid options are %s" % (field.data, ','.join(VALID_FORMATS)))
    
    def validate_hl(self, field):
        for hl in field.data:
            if not len(hl):
                continue
            if re.search('[^a-z\_\:', hl, re.I):
                raise ValidationError("Invalid highlight input: %s. Format is field[:count].")
            hl = hl.split(':')
            if hl[0] not in config.API_SOLR_FIELDS:
                raise ValidationError("Invalid highlight selection: %s is not a selectable field" % hl[0])
            if len(hl) > 1:
                if re.search('[^\d]', hl[1]):
                    raise ValidationError("Invalid highlight option: %s. Value for count must be integer." % hl[1])
    
    def validate_sort(self, field):
        """
        checks that sort input contains both a valid sorting option and direction
        """
        if not len(field.data):
            return
        try:
            sort, direction = field.data.split()
        except:
            raise ValidationError("Invalid sort option: you must specify a type (%s) and direction (%s)" % \
                                  (','.join(config.SOLR_SORT_OPTIONS.keys(), ','.join(SORT_DIRECTIONS))))
        if sort not in config.SOLR_SORT_OPTIONS:
            raise ValidationError("Invalid sort type. Valid options are %s" % ','.join(config.SOLR_SORT_OPTIONS.keys()))
        if direction not in SORT_DIRECTIONS:
            raise ValidationError("Invalid sort direction. Valid options are %s" % ','.join(SORT_DIRECTIONS))
    
    def validate_facet(self, field):
        for facet in field.data:
            if not len(facet):
                continue
            if re.search('[^a-z\_\:', facet, re.I):
                raise ValidationError("Invalid facet input: %s. Format is field[:limit[:min]].")
            facet = facet.split(':')
            if facet[0] not in config.API_SOLR_FACET_FIELDS:
                raise ValidationError("Invalid facet selection: %s is not a facetable field" % facet[0])
            if len(facet) > 1:
                for opt in facet[1:]:
                    if re.search('[^\d]', opt):
                        raise ValidationError("Invalid facet options: %s. Values for limit and min must be integers." % opt)
    
    def validate_filter(self, field):
        for filter in field.data:
            if not len(filter):
                continue
            try:
                field,query = filter.split(':')
            except ValueError: # too many/few values to split
                raise ValidationError("Invalid filter: %s. Format should be 'field:value'" % filter)
            if field not in config.API_SOLR_FIELDS:
                raise ValidationError("Invalid filter field selection: %s is not a queryable field" % field)
            
    