'''
Created on Jul 16, 2013

@author: ehenneken
'''

from .forms import CitationHelperInputForm
from .forms import MetricsInputForm
from flask import (Blueprint, render_template, flash, request, jsonify, g, current_app as app)
from flask import Response
from werkzeug.datastructures import Headers
import os
import simplejson as json
from adsabs.core.form_functs import is_submitted_cust
from config import config #the global config object
from .biblio_functions import get_suggestions
from .metrics_functions import generate_metrics
from .metrics_functions import legacy_format
from .utils import export_metrics
from .utils import get_publications_from_query
from .errors import CitationHelperCannotGetResults

__all__ = ['bibutils_blueprint', 'index_bibutils', 'citation_helper','metrics']

bibutils_blueprint = Blueprint('bibutils', __name__, template_folder="templates", static_folder="static", url_prefix='/bibutils')

@bibutils_blueprint.route('/', methods=('GET','POST'))
def index_bibutils():
    """
    Entry point of input for ADS Bibliographic Utilities: currently only Citation Helper
    """
    return render_template('index_bibutils.html', page_var='ADS Bibliographic Utilities')

@bibutils_blueprint.route('/citation_helper', methods=('GET','POST'))
def citation_helper(**args):
    """
    Entry point of input for Citation Helper: form to input bibcodes
    """
    form = CitationHelperInputForm()
    # If we were called from results form, get bibcodes
    # from URL
    try:
        bibcodes = request.args.getlist('bibcode')
    except:
        bibcodes = []
    results = None
    format = ''
    # check if we were called with bibcodes
    if 'bibcodes' in args:
        bibcodes = args['bibcodes']
        format = 'json'
    if 'Nsuggest' in args:
        number_of_suggestions = args['Nsuggest']
    else:
        number_of_suggestions = config.BIBUTILS_DEFAULT_SUGGESTIONS
    if is_submitted_cust(form):
        # the form was submitted, so get the contents from the submit box
        # make sure we have a list of what seem to be bibcodes
        bibcodes = map(lambda a: str(a).strip(), form.bibcodes.data.strip().split('\n'))
        bibcodes = filter(lambda a: len(a) == 19, bibcodes)
        # no bibcodes? display message and re-display input form
        if len(bibcodes) == 0:
            flash('Citation Helper returned no results. Reason: No bibcodes were supplied')
            return render_template('citation_helper.html', form=form)
        # get the maximum number of records to use
        try:
            number_of_records = int(form.numRecs.data)
        except:
            number_of_records = config.MAX_EXPORTS['citation_helper']
        # get the maximum number of suggestions
        try:
            number_of_suggestions = int(form.return_nr.data)
        except:
            number_of_suggestions = config.BIBUTILS_DEFAULT_SUGGESTIONS
        layout = form.layout.data or "NO"
        app.logger.info('ID %s. Requesting %s suggestions. Input: %s'%(g.user_cookie_id,number_of_suggestions,str(bibcodes)))
    if len(bibcodes) > 0:
        # we have all we need, so it's time to get the suggestions
        try:
            suggestions = get_suggestions(bibcodes=bibcodes,Nsuggest=number_of_suggestions)
        except CitationHelperCannotGetResults, e:
            # if we end up here, something went boink during data retrieval
            app.logger.error('ID %s. Unable to get results! (%s)' % (g.user_cookie_id,e))
        # if we got results, return them, otherwise say that we did not find any,
        # and re-display the input form.
        # no suggestions are possible if there are no 'friends-of-friends'
        if len(suggestions) > 0:
            app.logger.info('ID %s. Found %s suggestions. Suggestions: %s'%(g.user_cookie_id,len(suggestions),str(suggestions)))
            if format == 'json':
                return jsonify(suggestions=suggestions)
            else:
                return render_template('citation_helper_results.html', page_var='Citation Helper Results', results=suggestions, include_layout=layout)
        else:
            app.logger.info('ID %s. No suggestions found.'%g.user_cookie_id)
            if layout == 'NO':
                return render_template('citation_helper_no_results.html')
            else:
                flash('Citation Helper returned no results. Reason: No suggestions were found.')
    return render_template('citation_helper.html', form=form)

@bibutils_blueprint.route('/metrics', methods=('GET','POST'))
def metrics(**args):
    """
    Entry point of input for Metrics: form to input bibcodes
    """
#     query = request.args.get('q', None)
    form = MetricsInputForm()
    # If we were called from results form, get bibcodes
    # from URL
    try:
        bibcodes = request.args.getlist('bibcode')
    except:
        bibcodes = []
    if request.method == 'POST':
        export_id = request.form.get('exportid','')
        if export_id:
            export_file = config.METRICS_TMP_DIR + '/' + export_id
            try:
                xls_file = open(export_file)
            except Exception, err:
                app.logger.error('ID %s. Unable retrieve saved metrics file: %s! (%s)' % (g.user_cookie_id,export_file,err))
            response = Response()
            response.status_code = 200
            xls_str = xls_file.read()
            xls_file.close()
            response.data = xls_str
            response_headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': 'text/xls; charset=UTF-8',
            'Content-Disposition': 'attachment; filename=\"Metrics.xls\";',
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
            })
            response.headers = response_headers
            response.set_cookie('fileDownload', 'true', path='/')
            return response

    results = None
    format = ''
    layout = 'YES'
    if 'bibcodes' in args:
        bibcodes = args['bibcodes']
        format = 'json'
    if is_submitted_cust(form):
        try:
            layout = form.layout.data
        except:
            layout = 'NO'
        # get the maximum number of records to use
        try:
            number_of_records = int(form.numRecs.data)
        except:
            number_of_records = config.MAX_EXPORTS['metrics']
        # the form was submitted, so get the contents from the submit box
        # make sure we have a list of what seem to be bibcodes
        query_bibcodes = []
        try:
            bibcodes = filter(lambda b: len(b) == 19, map(lambda a: str(a).strip(), form.bibcodes.data.strip().split('\n')))
        except:
            bibcodes = []
        if len(bibcodes) == 0:
            try:
                query_par = str(form.current_search_parameters.data.strip())
                query = json.loads(query_par)['q']
                sort  = json.loads(query_par)['sort']
                bibcodes = get_publications_from_query(query)[:number_of_records]
            except:
                bibcodes = []
#        if len(query_bibcodes) == 0:
#            bibcodes = map(lambda a: str(a).strip(), form.bibcodes.data.strip().split('\n'))
#        else:
#            bibcodes = query_bibcodes[:config.METRICS_MAX_EXPORT]
        bibcodes = filter(lambda a: len(a) == 19, bibcodes)
        # no bibcodes? display message and re-display input form
        if len(bibcodes) == 0:
            flash('Metrics returned no results. Reason: No valid bibcodes were supplied')
            return render_template('metrics.html', form=form)
    if len(bibcodes) > 0:
        # we have a list of bibcodes, so start working
        try:
            results = generate_metrics(bibcodes=bibcodes, fmt=format)
        except Exception, err:
            app.logger.error('ID %s. Unable to get results! (%s)' % (g.user_cookie_id,err))
            return render_template('metrics_no_results.html', include_layout=layout)
    if results:
        try:
            excel_id = export_metrics(results)
        except:
            excel_id = ''
        mode = 'normal'
        if len(bibcodes) == 1:
            mode = 'singlebibcode'
        results['mode'] = mode
        if format == 'json':
            return jsonify(metrics=results)
        else:
            return render_template('metrics_results.html', results=results, include_layout=layout, export_id=excel_id)
    return render_template('metrics.html', form=form)
