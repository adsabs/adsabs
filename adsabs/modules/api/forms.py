'''
Created on Sep 19, 2012

@author: jluker
'''

import re

from flask import g
from wtforms import Form, Field, fields, ValidationError, validators

from renderers import VALID_FORMATS
from config import config

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 1000
SORT_DIRECTIONS = ['asc','desc']

from flask.ext.pushrod import Pushrod #@UnresolvedImport
Pushrod.format_arg_name = 'fmt'

class RepeatableField(Field):
    """
    Necessary as WTForms default Field classes don't allow for repeated values
    for a single field
    """
    def process_formdata(self, valuelist):
        self.data = valuelist
        
class ApiQueryForm(Form):
    dev_key = fields.TextField(validators=[validators.Required()])
    fl = fields.TextField()
    fmt = fields.TextField()
    hl = RepeatableField()
    q = fields.TextField()
    rows = fields.IntegerField()
    start = fields.IntegerField()
    sort = fields.TextField()
    facet = RepeatableField()
    filter = RepeatableField()
    hlq = fields.TextField()

    def validate_hlq(self, field):
        return self.validate_q(field)
    
    def validate_q(self, field):
        """
        just checks for min/max length so far
        TODO: maybe do closer inspection of the query syntax?
        """
        if not len(field.data):
            return
        if len(field.data) < MIN_QUERY_LENGTH:
            raise ValidationError("%s input must be at least %s characters" % (field.name, MIN_QUERY_LENGTH))
        if len(field.data) > MAX_QUERY_LENGTH:
            raise ValidationError("%s input must be at no more than %s characters" % (field.name, MAX_QUERY_LENGTH))
        
    def validate_fl(self, field):
        """
        checks that input is a comma separated list of field names
        """
        if not len(field.data):
            return
        if re.search('[^a-z\,\_]', field.data, re.I):
            raise ValidationError("Invalid field selection: value must be a comma-separated (no whitespace) list of field names")
        for field_name in field.data.split(','):
            if field_name not in config.API_SOLR_DEFAULT_FIELDS + config.API_SOLR_EXTRA_FIELDS:
                raise ValidationError("Invalid field selection: %s is not a selectable field" % field_name)
    
    def validate_fmt(self, field):
        if not len(field.data):
            return
        if field.data not in VALID_FORMATS:
            raise ValidationError("Invalid format: %s. Valid options are %s" % (field.data, ','.join(VALID_FORMATS)))

    def validate_hl(self, field):
        for hl in field.data:
            if not len(hl):
                continue
            if re.search('[^0-9a-z\_\:]', hl, re.I):
                raise ValidationError("Invalid highlight input: %s. Format is field[:count].")
            hl = hl.split(':')
            if hl[0] not in config.API_SOLR_HIGHLIGHT_FIELDS:
                raise ValidationError("Invalid highlight selection: %s is not a selectable field" % hl[0])
            if len(hl) > 1:
                if not hl[1].isdigit():
                    raise ValidationError("Invalid highlight option: %s. Value for count must be integer." % hl[1])
            if len(hl) > 2:
                raise ValidationError("Invalid highlight option: %s. Too many options.")

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
                                  (','.join(config.SEARCH_SORT_OPTIONS_MAP.keys()), ','.join(SORT_DIRECTIONS)))
        if sort not in config.SEARCH_SORT_OPTIONS_MAP:
            raise ValidationError("Invalid sort type. Valid options are %s" % ','.join(config.SEARCH_SORT_OPTIONS_MAP.keys()))
        if direction not in SORT_DIRECTIONS:
            raise ValidationError("Invalid sort direction. Valid options are %s" % ','.join(SORT_DIRECTIONS))

    def validate_facet(self, field):
        for facet in field.data:
            if not len(facet):
                continue
            if re.search('[^0-9a-z\_\:]', facet, re.I):
                raise ValidationError("Invalid facet input: %s. Format is field[:limit[:min]].")
            facet = facet.split(':')
            if facet[0] not in config.API_SOLR_FACET_FIELDS:
                raise ValidationError("Invalid facet selection: %s is not a facetable field" % facet[0])
            if len(facet) > 3:
                raise ValidationError("Invalid facet option: %s. Too many options.")
            if len(facet) > 1:
                for opt in facet[1:]:
                    if not opt.isdigit():
                        raise ValidationError("Invalid facet options: %s. Values for limit and min must be integers." % opt)

    def validate_filter(self, field):
        for filter in field.data:
            if not len(filter):
                continue
            filter = filter.split(':')
            if len(filter) > 1:
                field_name = filter[0]
                query = filter[1]
            else:
                field_name = None
                query = filter[0]
            if field_name and field_name not in config.API_SOLR_DEFAULT_FIELDS + config.API_SOLR_EXTRA_FIELDS:
                raise ValidationError("Invalid filter field selection: %s is not a queryable field" % field_name)
            if len(query) > MAX_QUERY_LENGTH:
                raise ValidationError("%s input must be at no more than %s characters" % (field_name, MAX_QUERY_LENGTH))
